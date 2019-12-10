import pickle
import sys
import time
from queue import Queue
from threading import Thread

import cv2
import dlib
import numpy as np
import scipy
from sklearn.preprocessing import normalize

from persist import worker_persist
from sort import Sort, convert_x_to_bbox
from utils import FPS, VideoStream, preprocess, get_face_from_frame, get_pos_from_rect

THRESHOLD = 0.25
UNKNOWN = 'Unknown'
SKIP_FRAME = 5
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_BLACK = (0, 0, 0)

predictor_path = "shape_predictor_5_face_landmarks.dat"
face_rec_model_path = "dlib_face_recognition_resnet_model_v1.dat"

predictor = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)
detector = dlib.get_frontal_face_detector()

classifier = pickle.load(open('cclf_linearsvc_21class.pkl', 'rb'))
label_encoder = pickle.load(open('lb_21class.pkl', 'rb'))
# stream = VideoStream("..\\dataset\\video\\output_1.mp4").start()
persist_queue = Queue()
persistence_worker = Thread(target=worker_persist, args=(persist_queue,), daemon=True)
persistence_worker.start()
stream = VideoStream(0).start()
time.sleep(2)

sort_tracker = Sort(max_age=20, min_hits=1)

if __name__ == "__main__":
    dets = np.array([])
    labels = np.array([])
    probs_max = np.array([])
    faces = np.array([])
    fps = FPS().start()
    while True:
        ret, frame = stream.read()
        if not ret:
            continue
        frame = cv2.resize(frame, (1280, 720))
        if fps._numFrames % SKIP_FRAME == 0:
            rects = detector(frame, 0)
            dets = np.array([get_pos_from_rect(rect) for rect in rects])
            labels = np.empty(len(rects))
            probs_max = np.empty(len(rects))
            faces = np.array([get_face_from_frame(det, frame) for det in dets])
            frame_processed = preprocess(frame)[..., ::-1]
            if len(rects) > 0:
                embeddings = []
                for i, rect in enumerate(rects):
                    shape = predictor(frame_processed, rect)
                    face_descriptor = facerec.compute_face_descriptor(frame_processed, shape, 1,
                                                                      0.4)
                    face_descriptor = np.array(face_descriptor)
                    embeddings.append(face_descriptor)
                embeddings = np.array(embeddings)
                embeddings = normalize(embeddings)

                probs = classifier.predict_proba(embeddings)
                probs_max = np.max(probs, axis=1)
                unknown_index = np.where(probs_max < THRESHOLD)[0]
                prediction = np.argmax(probs, axis=1)
                labels = label_encoder.inverse_transform(prediction)
                labels[unknown_index] = UNKNOWN

        probs_max = np.round(probs_max, 4)
        sort_tracker.update(dets, labels, probs_max, faces, persist_queue)
        for tracker in sort_tracker.trackers:
            bbox = convert_x_to_bbox(tracker.kf.x[:4, :]).astype('int')
            (left, top, right, bottom) = bbox.flatten()
            left = max(0, left)
            top = max(0, top)
            right = min(right, frame.shape[1])
            bottom = min(bottom, frame.shape[0])
            nama = tracker.mode_names()
            probs = round(tracker.mean_probs() * 100, 4)
            text = "{}  {}%".format(nama, probs) if nama != UNKNOWN else UNKNOWN
            color = COLOR_GREEN if nama != UNKNOWN else COLOR_RED
            cv2.rectangle(frame, (left, top), (right, bottom), color, 4)
            cv2.putText(frame, text, (left - 10, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                        COLOR_WHITE, 4)

        cv2.putText(frame, "{:.1f} FPS".format(fps.fps()), (1100, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, COLOR_BLACK, 2)
        current_time = time.ctime()
        cv2.putText(frame, current_time, (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOR_BLACK, 2)
        cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if 'q' == chr(key):
            break
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # sys.stdout.buffer.write(frame.tobytes())
        fps.update()

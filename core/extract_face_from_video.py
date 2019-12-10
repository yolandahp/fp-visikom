import os
import time
from glob import glob
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from queue import Queue
from threading import Thread
from typing import NamedTuple

import cv2
import dlib
import numpy as np
from tqdm import tqdm

FRAME_STEPS = 20
storage = Queue(maxsize=500)


class Frame(NamedTuple):
    array: np.ndarray
    video_name: str
    num_frame: int


def batch(data: list, batch_size: int = 4):
    size = len(data)
    start = 0
    while start < size:
        stop = start + batch_size
        yield data[start:stop]
        start = stop


def worker_video_reader(video_path):
    video_name = video_path.split(os.sep)[-1]
    video_name = video_name.split('.')[:-1]
    video_name = '_'.join(video_name)
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    num_frame = 0
    while (ret):
        if num_frame % FRAME_STEPS == 0:
            attr = {
                'array': frame,
                'video_name': video_name,
                'num_frame': num_frame
            }
            frame = Frame(**attr)
            storage.put(frame)
            # break
        ret, frame = cap.read()
        num_frame += 1
    return


def get_pos_from_rect(rect):
    return (rect.left(), rect.top(), rect.right(), rect.bottom())


def extract(frame: Frame):
    img = frame.array
    video_name = frame.video_name
    num_frame = frame.num_frame
    img_name_prefix = "{}_{}".format(video_name, num_frame)

    detector = dlib.get_frontal_face_detector()
    rects = detector(img, 1)
    dets = [get_pos_from_rect(rect) for rect in rects]
    for i, (left, top, right, bottom) in enumerate(dets):
        face = img[top:bottom, left:right]
        filename = "{}_{}.png".format(img_name_prefix, i)
        filename = os.path.join("outputs_new", filename)
        cv2.imwrite(filename, face)


if __name__ == "__main__":
    video_names = glob("dataset{sep}**{sep}*.mp4".format(sep=os.sep))
    print(video_names)
    batch_size = 4
    for i, video_names_batch in enumerate(batch(video_names, batch_size=4)):
        threads = []
        for video_name in video_names_batch:
            thread = Thread(target=worker_video_reader, args=(video_name, ))
            thread.start()
            threads.append(thread)
        is_alive = [thread.is_alive() for thread in threads]
        time.sleep(5)
        while any(is_alive):
            desc = "Extract batch {} threads {}".format(i, sum(is_alive))
            size = storage.qsize()
            frames = [storage.get() for _ in range(size)]
            with Pool(processes=cpu_count() - 1) as p:
                with tqdm(total=len(frames), desc=desc) as pbar:
                    for _, _ in tqdm(enumerate(p.imap(extract, frames))):
                        pbar.update()
            is_alive = [thread.is_alive() for thread in threads]
    desc = "Extract batch last"
    size = storage.qsize()
    frames = [storage.get() for _ in range(size)]
    with Pool(processes=cpu_count() - 1) as p:
        with tqdm(total=len(frames), desc=desc) as pbar:
            for _, _ in tqdm(enumerate(p.imap(extract, frames))):
                pbar.update()
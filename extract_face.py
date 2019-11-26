import os
from multiprocessing import cpu_count
from multiprocessing.pool import Pool

import cv2
import dlib
import numpy as np

from tqdm import tqdm


def get_pos_from_rect(rect):
    return (rect.left(), rect.top(), rect.right(), rect.bottom())


def extract(path: str):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    img_name = path.split(os.sep)[-2:]
    img_name[-1] = img_name[-1].split(".")[0]
    img_name_prefix = "_".join(img_name)
    detector = dlib.get_frontal_face_detector()
    rects = detector(img, 1)
    dets = [get_pos_from_rect(rect) for rect in rects]
    for i, (left, top, right, bottom) in enumerate(dets):
        face = img[top:bottom, left:right]
        filename = "{}_{}.png".format(img_name_prefix, i)
        filename = os.path.join("faces_gray_0", filename)
        cv2.imwrite(filename, face)


if __name__ == "__main__":
    dataset_folder = os.path.join("frames")
    videos = os.listdir(dataset_folder)
    frames = []
    for video in videos:
        video_path = os.path.join(dataset_folder, video)
        frame = os.listdir(video_path)
        frame = [os.path.join(video_path, f) for f in frame]
        frames.extend(frame)
    with Pool(processes=cpu_count() - 1) as p:
        with tqdm(total=len(frames)) as pbar:
            for _, _ in tqdm(enumerate(p.imap(extract, frames))):
                pbar.update()
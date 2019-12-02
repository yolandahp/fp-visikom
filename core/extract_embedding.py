import os
from multiprocessing import cpu_count
from multiprocessing.pool import Pool

import cv2
import dlib
import h5py
import numpy as np
import pandas as pd
from tqdm import tqdm

predictor_path = "shape_predictor_5_face_landmarks.dat"
face_rec_model_path = "dlib_face_recognition_resnet_model_v1.dat"

sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)


def extract(img_path: str) -> np.ndarray:
    img = dlib.load_rgb_image(img_path)
    left, top, bottom, right = 0, 0, img.shape[0], img.shape[1]
    det = dlib.rectangle(left=left, top=top, right=right, bottom=bottom)
    shape = sp(img, det)
    face_descriptor = np.array(
        facerec.compute_face_descriptor(img, shape, 1, 0.4))

    return face_descriptor.flatten()


if __name__ == "__main__":
    hf = h5py.File('dataset.h5', 'w')
    for name in ['train', 'test']:
        df = pd.read_csv('sample_{}.csv'.format(name))
        base_dir = name
        paths = base_dir + os.sep + df['label'] + os.sep + df[
            'sequence'] + os.sep + df['path']
        paths = paths.values.tolist()
        res = []
        with Pool(processes=cpu_count() - 1) as p:
            with tqdm(total=len(paths), desc='Encode {}'.format(name)) as pbar:
                for _, encoding in tqdm(enumerate(p.imap(extract, paths))):
                    pbar.update()
                    res.append(encoding)
            res = np.array(res)
            print(res.shape)
            hf.create_dataset(name, data=res)
    hf.close()

import os
import time

import cv2
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm


# https://stackoverflow.com/a/56909036
# Automatic brightness and contrast optimization with optional histogram clipping
def automatic_brightness_and_contrast(image, clip_hist_percent=1):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Calculate grayscale histogram
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_size = len(hist)

    # Calculate cumulative distribution from the histogram
    accumulator = []
    accumulator.append(float(hist[0]))
    for index in range(1, hist_size):
        accumulator.append(accumulator[index - 1] + float(hist[index]))

    # Locate points to clip
    maximum = accumulator[-1]
    clip_hist_percent *= (maximum / 100.0)
    clip_hist_percent /= 2.0

    # Locate left cut
    minimum_gray = 0
    while accumulator[minimum_gray] < clip_hist_percent:
        minimum_gray += 1

    # Locate right cut
    maximum_gray = hist_size - 1
    while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
        maximum_gray -= 1

    # Calculate alpha and beta values
    alpha = 255 / (maximum_gray - minimum_gray)
    beta = -minimum_gray * alpha

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)


def process_image(image_path: str):
    image = cv2.imread(image_path)
    processed, _, _ = automatic_brightness_and_contrast(image)
    return processed


SRC_DIR = "labeled"
DST_DIR = "labeled_proc"
labels = os.listdir(SRC_DIR)

for label in tqdm(labels, desc="Labels"):
    label_path = os.path.join(SRC_DIR, label)
    dst_label_path = os.path.join(DST_DIR, label)
    os.makedirs(dst_label_path, exist_ok=True)

    filenames = os.listdir(label_path)
    for filename in tqdm(filenames, desc="images"):
        full_path = os.path.join(label_path, filename)
        dest_path = os.path.join(dst_label_path, filename)
        processed = process_image(full_path)
        cv2.imwrite(dest_path, processed)

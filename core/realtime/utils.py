import datetime
import time
from queue import Queue
from threading import Thread
from typing import Optional, Tuple, Union

import cv2
import numpy as np


class FPS:

    def __init__(self):
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        self._end = datetime.datetime.now()

    def update(self):
        self._numFrames += 1

    def elapsed(self):
        return (datetime.datetime.now() - self._start).total_seconds()

    def fps(self):
        return self._numFrames / self.elapsed()


class VideoStream:

    def __init__(self, src: Union[str, int]):
        self.q = Queue(maxsize=0)
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self._numFrames = 0
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()
            self._numFrames += 1
            # time.sleep(1 / 20)

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        return self.grabbed, self.frame

    def release(self):
        self.stopped = True


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
    '''
    # Calculate new histogram with desired range and show histogram 
    new_hist = cv2.calcHist([gray],[0],None,[256],[minimum_gray,maximum_gray])
    plt.plot(hist)
    plt.plot(new_hist)
    plt.xlim([0,256])
    plt.show()
    '''

    auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return (auto_result, alpha, beta)


def preprocess(image: np.ndarray):
    processed, _, _ = automatic_brightness_and_contrast(image)
    return image


def get_pos_from_rect(rect):
    return (rect.left(), rect.top(), rect.right(), rect.bottom())


def get_face_from_frame(bbox, frame: np.ndarray, padding: float = 0.4) -> np.ndarray:
    left, top, right, bottom = bbox
    width = right - left
    height = bottom - top

    width_pad = int(padding * width)
    height_pad = int(padding * height)

    left -= width_pad
    right += width_pad
    top -= height_pad
    bottom += height_pad

    left = max(0, left)
    top = max(0, top)
    right = min(right, frame.shape[1] - 1)
    bottom = min(bottom, frame.shape[0] - 1)

    face = frame[top:bottom, left:right]
    return face
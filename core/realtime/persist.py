import datetime
import os
import secrets
from queue import Queue
from typing import NamedTuple

import cv2
import imutils
import numpy as np
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

load_dotenv('.env')

DB_URI = 'mysql+mysqlconnector://{user}:{password}@{host}/{database}'.format(
    user=os.getenv('DB_USERNAME'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    database=os.getenv('DB_DATABASE'))

IMAGE_PATH = os.getenv('IMAGE_PATH')
WEB_PATH = '../../web/public'
engine = create_engine(DB_URI)

Session = sessionmaker(bind=engine)
Base = declarative_base()


class Person(NamedTuple):
    image: np.ndarray
    identity: str
    probability: float
    time: datetime.datetime


class Deteksi(Base):
    __tablename__ = 'deteksi'

    id = Column(Integer, primary_key=True)
    nama = Column(String(50))
    waktu = Column(DateTime)
    probabilitas = Column(Float)
    gambar = Column(String(100))

    def __init__(self, nama, waktu, probabilitas, gambar):
        self.nama = nama
        self.waktu = waktu
        self.probabilitas = probabilitas
        self.gambar = gambar


# Base.metadata.create_all(bind=engine)


def worker_persist(queue: Queue):
    while True:
        try:
            data: Person = queue.get()
            image = data.image
            image = imutils.resize(image, width=200)
            filename = '{}.png'.format(secrets.token_urlsafe(16))
            image_path = os.path.join(WEB_PATH, IMAGE_PATH, filename)
            cv2.imwrite(image_path, image)

            path_saved = os.path.join(IMAGE_PATH, filename)
            path_saved = path_saved.replace(os.sep, '/')
            session = Session()
            deteksi = Deteksi(data.identity, data.time, data.probability,
                              path_saved)
            session.add(deteksi)
            session.commit()
            session.close()
        except Exception as e:
            pass
            # print(repr(e))

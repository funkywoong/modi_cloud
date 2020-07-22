import os
import socket
import numpy as np
import h5py
import json

from joblib import load, dump
from io import BytesIO
from socket import getdefaulttimeout

class MLCodec():

    @staticmethod
    def model_type(target):
        if 'keras' in str(type(target)):
            return 'keras'
        elif 'sklearn' in str(type(target)):
            return 'sklearn'

    @staticmethod
    def parse_data(target):
        if isinstance(target, bytes):
            return target
        if isinstance(target, dict):
            return '{}{}'.format('DICT', json.dumps(target)).encode('utf-8')
        buf = BytesIO()
        if isinstance(target, np.ndarray):
            np.save(buf, target, allow_pickle=True)
        elif 'keras' in str(type(target)):
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            from tensorflow.keras.models import save_model
            with h5py.File(buf, 'w') as f:
                save_model(target, f, include_optimizer=True)
        elif 'sklearn' in str(type(target)):
            dump(target, buf)
        buf.seek(0)
        
        return buf.read()

    @staticmethod
    def load_data(target):
        buf = BytesIO()
        buf.write(target)
        buf.seek(0)
        data_type = buf.read()[:-3]
        buf.seek(0)
        if b'NUMPY' in data_type:
            return np.load(buf)
        elif b'sklearn' in data_type:
            return load(buf)
        elif b'HDF' in data_type:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            from tensorflow.keras.models import load_model
            with h5py.File(buf, 'r') as f:
                given_model = load_model(f)
            return given_model
        elif b'DICT' in data_type:
            return json.loads(buf.read()[4:].decode('utf-8'))
        else:
            return None

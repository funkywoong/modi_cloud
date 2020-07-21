import os
import socket
import numpy as np
import h5py

from joblib import load, dump
from io import BytesIO
from socket import getdefaulttimeout

class MLCodec():

    @staticmethod
    def parse_data(target):
        if isinstance(target, bytes):
            return target
        buf = BytesIO()
        if isinstance(target, np.ndarray):
            np.save(buf, target, allow_pickle=True)
        elif 'keras' in str(type(target)):
            # os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            # from tensorflow.keras.models import save_model
            # with h5py.File(buf, 'w') as f:
            #     save_model(target, f, include_optimizer=True)
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            from tensorflow.keras.models import model_from_config
            c = target.get_config()
            print(c)
        elif 'sklearn' in str(type(target)):
            dump(target, buf)
        buf.seek(0)
        
        return buf.read()

    @staticmethod
    def load_data(target: BytesIO):
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
        else:
            return None
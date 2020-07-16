from __future__ import print_function

import logging, os
import grpc
import h5py
import numpy as np
import numpy as np
import sys

from io import BytesIO 
from joblib import load, dump

import util.modi_ai_cloud_pb2 as pb2
import util.modi_ai_cloud_pb2_grpc as pb2_grpc

#example code
from example.test.test import gen_data, gen_model

def __parse_data(target):
    if isinstance(target, bytes):
        return target
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

def run():

    # X_train, X_valid, X_test, y_train, y_valid, y_test = gen_data()
    model = gen_model()
    # X_train = __parse_data(X_train)
    # y_train = __parse_data(y_train)
    model = __parse_data(model)
    # print(sys.getsizeof(X_train))
    # print(sys.getsizeof(y_train))
    # print(sys.getsizeof(model))
    tmp_train_list = np.array([1, 2, 3, 4])
    tmp_train_list = __parse_data(tmp_train_list)
    tmp_label_list = np.array([5, 6, 7, 8])
    tmp_label_list = __parse_data(tmp_label_list)

    with grpc.insecure_channel('ec2-15-164-216-238.ap-northeast-2.compute.amazonaws.com:8000') as channel:
        client_stub = pb2_grpc.Data_Model_HandlerStub(channel)
        # response_transfer = client_stub.TransferComplete(
        #     pb2.TransferCompleteSend(ask_transfer=1)
        # )
        response_train = client_stub.SendObjects(
            pb2.ObjectsSend(
                train_array=tmp_train_list, label_array=tmp_label_list, model=model)
        )
        print('out request')

    print("Label handler client received: ", response_train)
 
if __name__ == '__main__':
    logging.basicConfig()
    run()
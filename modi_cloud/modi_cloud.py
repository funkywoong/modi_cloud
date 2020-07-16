from __future__ import print_function

import logging, os
import grpc
import h5py
import numpy as np
import numpy as np
import sys

from io import BytesIO 
from joblib import load, dump
from util.mlcodec import MLCodec as codec

import util.modi_ai_cloud_pb2 as pb2
import util.modi_ai_cloud_pb2_grpc as pb2_grpc

#example code
from example.test.test import gen_data, gen_model

def run():

    X_train, X_valid, X_test, y_train, y_valid, y_test = gen_data()
    model = gen_model()
    X_train = codec.parse_data(X_train)
    y_train = codec.parse_data(y_train)
    model = codec.parse_data(model)
    print(sys.getsizeof(X_train))
    print(sys.getsizeof(y_train))
    print(sys.getsizeof(model))
    # tmp_train_list = np.array([1, 2, 3, 4])
    # tmp_train_list = codec.parse_data(tmp_train_list)
    # tmp_label_list = np.array([5, 6, 7, 8])
    # tmp_label_list = codec.parse_data(tmp_label_list)

    with grpc.insecure_channel('ec2-15-164-216-238.ap-northeast-2.compute.amazonaws.com:8000') as channel:
        client_stub = pb2_grpc.Data_Model_HandlerStub(channel)
        # response_transfer = client_stub.TransferComplete(
        #     pb2.TransferCompleteSend(ask_transfer=1)
        # )
        response_train = client_stub.SendObjects(
            pb2.ObjectsSend(
                train_array=X_train, label_array=y_train, model=model)
        )
        print('out request')
    
    trained_model = codec.load_data(response_train.trained_model)
    print("Label handler client received: ", trained_model)
 
if __name__ == '__main__':
    logging.basicConfig()
    run()
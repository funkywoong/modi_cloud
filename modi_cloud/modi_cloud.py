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

class MODI_cloud():
    
    def __init__(self, train_data, label_data, model):
        self.__X_train = train_data
        self.__y_train = label_data
        self.__model = model

        logging.basicConfig()
        self.fit()

    def fit(self):
        X_train = codec.parse_data(self.__X_train)
        y_train = codec.parse_data(self.__y_train)
        model = codec.parse_data(self.__model)

        with grpc.secure_channel('ec2-15-164-216-238.ap-northeast-2.compute.amazonaws.com:8000') as channel:
            client_stub = pb2_grpc.Data_Model_HandlerStub(channel)

            response_train = client_stub.SendObjects(
                pb2.ObjectsSend(
                    train_array=X_train, label_array=y_train, model=model)
            )
        trained_model = codec.load_data(response_train.trained_model)
        
        return trained_model

if __name__ == '__main__':
    X_train, X_valid, X_test, y_train, y_valid, y_test = gen_data()
    model = gen_model()

    model = MODI_cloud(X_train, y_train, model)
    loss_and_metrics = model.evaluate(X_test, y_test)
    print(loss_and_metrics)
    
 
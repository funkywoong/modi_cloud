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

class MODI_model():

    @staticmethod
    def fit(train_data, label_data, model):
        X_train = codec.parse_data(train_data)
        y_train = codec.parse_data(label_data)
        model = codec.parse_data(model)

        return MODI_model.__com_server(X_train, y_train, model)

    @staticmethod
    def __com_server(train_data, label_data, model):
        with grpc.insecure_channel('ec2-15-164-216-238.ap-northeast-2.compute.amazonaws.com:8000') as channel:
            client_stub = pb2_grpc.Data_Model_HandlerStub(channel)

            response_train = client_stub.SendObjects(
                pb2.ObjectsSend(
                    train_array=train_data, label_array=label_data, model=model)
            )
        trained_model = codec.load_data(response_train.trained_model)
        
        return trained_model

if __name__ == '__main__':
    X_train, X_valid, X_test, y_train, y_valid, y_test = gen_data()
    model = gen_model()

    model = MODI_model.fit(X_train, y_train, model)
    loss_and_metrics = model.evaluate(X_test, y_test)
    print(loss_and_metrics)
    
 
from __future__ import print_function

import logging, os, time, sys
import grpc
import h5py
import numpy as np
import numpy as np
import threading as th

# from IPython.display import clear_output
from io import BytesIO 
from joblib import load, dump
from modi_cloud.util.mlcodec import MLCodec as codec

import modi_cloud.util.modi_ai_cloud_pb2 as pb2
import modi_cloud.util.modi_ai_cloud_pb2_grpc as pb2_grpc

#example code
from modi_cloud.example.test.test import gen_data, gen_model

class MODI_model():

    def __init__(self, model):
        self.HOST_URL = 'ec2-15-164-216-238.ap-northeast-2.compute.amazonaws.com:8000'
        self.__client_stub = None
        self.__X_train = None
        self.__y_train = None
        self.__model = model
        self.__trns_flag = th.Event()
        self.__trained_model = None

    def fit(self, train_data, label_data):
        self.__X_train = codec.parse_data(train_data)
        self.__y_train = codec.parse_data(label_data)
        self.__model = codec.parse_data(self.__model)

        return self.__com_server()

    def __com_server(self):
        with grpc.insecure_channel(self.HOST_URL) as channel:
            self.__client_stub = pb2_grpc.Data_Model_HandlerStub(channel)

            req_train_th = th.Thread(target=self.__req_training, daemon=True)
            req_train_th.start()

            req_trns_th = th.Thread(target=self.__req_trns_complete, daemon=True)
            req_trns_th.start()

            req_std_th = th.Thread(target=self.__req_gpu_stdout, daemon=True)
            req_std_th.start()

            req_train_th.join()
            req_trns_th.join()
            req_std_th.join()
        
        return self.__trained_model

    def __req_training(self):
        response_train = self.__client_stub.SendObjects(
            pb2.ObjectsSend(
                train_array=self.__X_train, label_array=self.__y_train, model=self.__model
            )
        )

        self.__trained_model = codec.load_data(response_train.trained_model)

    def __req_trns_complete(self):
        response_transfer = self.__client_stub.TransferComplete(
            pb2.TransferCompleteSend(ask_transfer=1)
        )

        if response_transfer: self.__trns_flag.set()
        print(response_transfer.reply_transfer)

    def __req_gpu_stdout(self):

        self.__trns_flag.wait()
        input_stream = self.__client_stub.MonitorLearning(
            pb2.StdoutSend(ask_stdout=1)
        )

        while 1:
            try:
                item = next(input_stream).reply_stdout
                print(item)
                if item == 'End':
                    break
                time.sleep(0.05)
            except:
                break
            
if __name__ == '__main__':
    X_train, X_valid, X_test, y_train, y_valid, y_test = gen_data()
    model = gen_model()
    print(sys.getsizeof(X_train))
    print(sys.getsizeof(y_train))
    print(sys.getsizeof(model))
    # model = None

    modi_model = MODI_model(model)
    model = modi_model.fit(X_train, y_train)
    loss_and_metrics = model.evaluate(X_test, y_test)
    print(loss_and_metrics)
    
 

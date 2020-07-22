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
        self.__model = model
        self.__X_train = None
        self.__Y_train = None
        
        self.__model_type = codec.model_type(model)
        self.__client_stub = None
        self.__fit_param = dict()

        self.__trns_flag = th.Event()
        self.__trained_model = None

    def fit(self, train_data, label_data, **kwargs):
        self.__model = codec.parse_data(self.__model)
        self.__X_train = codec.parse_data(train_data)
        self.__y_train = codec.parse_data(label_data)

        try:
            self.__fit_param = self.__search_param(kwargs)
        except KeyError:
            print('학습 파라미터를 잘못 입력하였습니다. 다시 시도해주세요.')

        # TODO : keras / sklearn 마다 communication proto 재 정의
        if self.__model_type == 'keras':
            return self.__keras_fit()
        elif self.__model_type == 'sklearn':
            return self.__sklearn_fit()

    def __keras_fit(self):
        
        return self.__com_server()

    def __sklearn_fit(self):
        
        return self.__com_server()

    def __search_param(self, model_type, user_param):
        if model_type == 'keras':
            self.__search_keras_param(user_param)
        elif model_type == 'sklearn':
            self.__search_sklearn_param(user_param)

    def __search_keras_param(self, user_param):
        keras_param = {
            'batch_size' : None, 'epochs' : 1, 'verbose' : 1, 'callbacks' : None,
            'validation_split' : 0.0, 'validation_data' : None, 'shuffle' : True, 'class_weight' : None,
            'sample_weight' : None, 'initial_epoch' : 0, 'steps_per_epoch' : None,
            'validation_steps' : None, 'validation_batch_size' : None, 'validation_freq' : 1,
            'max_queue_size' : 10, 'workers' : 1, 'use_multiprocessing' : False
        }

        for key, new_value in user_param.items():
            keras_param[key] = new_value
        return keras_param

    def __search_sklearn_param(self):
        sklearn_param = {
            'sample_weight' = None
        }
        
        for key, new_value in user_param.items():
            sklearn_param[key] = new_value
        return sklearn_param

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
        elif response_transfer == -1:
            print('GPU 서버와의 연결이 성공하지 못햇습니다. 다시 시도해주세요.')
            sys.exit(0)

    def __req_gpu_stdout(self):
        
        self.__trns_flag.wait()
        input_stream = self.__client_stub.MonitorLearning(
            pb2.StdoutSend(ask_stdout=1)
        )

        while 1:
            try:
                item = next(input_stream).reply_stdout
                print(item, end='')
                if item == 'End':
                    break
                time.sleep(0.05)
            except:
                break
            
# if __name__ == '__main__':
#     X_train, X_valid, X_test, y_train, y_valid, y_test = gen_data()
#     model = gen_model()
#     print(sys.getsizeof(X_train))
#     print(sys.getsizeof(y_train))
#     print(sys.getsizeof(model))
#     # model = None

#     modi_model = MODI_model(model)
#     model = modi_model.fit(X_train, y_train)
#     loss_and_metrics = model.evaluate(X_test, y_test)
#     print(loss_and_metrics)
    
 
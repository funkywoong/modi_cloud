import time
import logging, os
import grpc
import h5py
import numpy as np
import threading as th

from joblib import load, dump
from concurrent import futures
from io import BytesIO
from util.mlcodec import MLCodec as codec

import util.modi_ai_cloud_pb2 as pb2
import util.modi_ai_cloud_pb2_grpc as pb2_grpc

MESSAGE_SIZE = 1024 * 1024 * 200

class Data_model_handler(pb2_grpc.Data_Model_HandlerServicer):

    def __watchdog(self):
        pass
        
    def SendObjects(self, request, context):

        print('in SendObjects')
        train_data = codec.load_data(request.train_array)
        label_data = codec.load_data(request.label_array)
        model = codec.load_data(request.model)

        if not self.__is_transfer_ok(train_data, label_data, model):
            return pb2.ModelReply(trained_model=None)

        hist, trained_model = self.__training(train_data, label_data, model)
        print(type(hist))
        print(type(trained_model))
        trained_model = codec.parse_data(trained_model)
        
        return pb2.ModelReply(trained_model=trained_model)

    def TransferComplete(self, request, context):

        return pb2.TransferCompleteReply(reply_transfer=-1)

    def __training(self, X_train, y_train, model):
        hist = model.fit(X_train, y_train, epochs=50, batch_size=32)

        return hist, model

    def __is_transfer_ok(self, train_data, label_data, model):
        return(
            train_data is not None and
            label_data is not None and
            model is not None
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=[
        ('grpc.max_send_message_length', MESSAGE_SIZE),
        ('grpc.max_receive_message_length', MESSAGE_SIZE)
    ])
    pb2_grpc.add_Data_Model_HandlerServicer_to_server(Data_model_handler(), server)
    server.add_insecure_port('[::]:8000')
    server.start()
    print('server start')
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()

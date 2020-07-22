import time
import logging, os, sys
import grpc
import h5py
import numpy as np
import threading as th

from joblib import load, dump
from concurrent import futures
from io import BytesIO, StringIO
from modi_cloud.util.mlcodec import MLCodec as codec

import modi_cloud.util.modi_ai_cloud_pb2 as pb2
import modi_cloud.util.modi_ai_cloud_pb2_grpc as pb2_grpc

MESSAGE_SIZE = 1024 * 1024 * 200

class Data_model_handler(pb2_grpc.Data_Model_HandlerServicer):

    def __init__(self):
        super().__init__()

        self.__trns_flag = th.Event()
        self.__trns_com_flag = False
        self.__train_flag = th.Event()
        self.__train_com_flag = False

        self.__old_stdout = None
        self.__new_stdout = None

    def __watchdog(self):
        pass
        
    def SendObjects(self, request, context):
        print('in SendObjects')
        model = codec.load_data(request.model)
        train_data = codec.load_data(request.train_array)
        label_data = codec.load_data(request.label_array)

        if not self.__is_transfer_ok(train_data, label_data, model):
            self.__trns_flag.set()
            return pb2.ModelReply(trained_model=None)
        self.__trns_com_flag = True
        self.__trns_flag.set()

        hist, trained_model = self.__training(train_data, label_data, model)
        trained_model = codec.parse_data(trained_model)
        
        return pb2.ModelReply(trained_model=trained_model)

    def TransferComplete(self, request, context):
        self.__trns_flag.wait(timeout=300)
        if (
            request.ask_transfer and 
            self.__trns_flag.is_set() and
            self.__trns_com_flag
        ):
            return pb2.TransferCompleteReply(reply_transfer=1)
        else:
            return pb2.TransferCompleteReply(reply_transfer=-1)

    def MonitorLearning(self, request, context):
        self.__train_flag.wait(timeout=300)
        def stream():
            while self.__train_flag.is_set():
                time.sleep(0.001)
                yield self.__new_stdout.getvalue()
        
        output_stream = stream()

        old_reply = str()
        while True:
            if request.ask_stdout and self.__train_flag.is_set():
                time.sleep(0.001)
                try:
                    new_reply = next(output_stream)
                    if old_reply != new_reply:
                        target_index = len(old_reply)
                        old_reply = new_reply
                        target_str = old_reply[target_index:]
                        yield pb2.StdoutReply(reply_stdout=target_str)
                except:
                    print('Generator raised StopIteration except')
                    break
                finally:
                    if self.__train_com_flag:
                        break
            else:
                pass
        output_stream.close()
        print('out')
        return pb2.StdoutReply(reply_stdout='End')

    def __training(self, X_train, y_train, model):
        self.__old_stdout = sys.stdout
        self.__new_stdout = StringIO()
        sys.stdout = self.__new_stdout

        self.__train_flag.set()
        hist = model.fit(X_train, y_train, epochs=5, batch_size=1)
        output = self.__new_stdout.getvalue()
        sys.stdout = self.__old_stdout

        self.__train_com_flag = True
        print(output)
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

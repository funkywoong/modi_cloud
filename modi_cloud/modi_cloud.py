import time
import logging
import grpc
import h5py
import numpy as np
import threading as th

from joblib import load, dump
from concurrent import futures
from io import BytesIO

import util.modi_ai_cloud_pb2 as pb2
import util.modi_ai_cloud_pb2_grpc as pb2_grpc

class Data_model_handler(pb2_grpc.Data_Model_HandlerServicer):

    def __init__(self):
        super().__init__()

        self.__trns_flag = th.Event()

    def SendObjects(self, request, context):

        train_data = self.__load_data(request.train_array)
        label_data = self.__load_data(request.label_array)
        model = self.__load_data(request.model)

        if not self.__is_transfer_ok(train_data, label_data, model):
            self.__trns_flag.set()

        tmp_reply = bytes(b'complete')
        print('bye')
        return pb2.ModelReply(trained_model=tmp_reply)

    def TransferComplete(self, request, context):
        if request.ask_transfer:
            self.__trns_flag.wait()

        return pb2.TransferCompleteReply(reply_transfer=-1)

            

        #TODO: training data by using given model

    def __is_transfer_ok(self, train_data, label_data, model):
        return(
            train_data is not None and
            label_data is not None and
            model is not None
        )

    def __load_data(self, target):
        buf = BytesIO()
        buf.write(target)
        buf.seek(0)
        data_type = buf.read()[:-3]
        buf.seek(0)
        if b'NUMPY' in data_type:
            return np.load(buf)
        elif b'sklearn' in data_type:
            return load(target)
        elif b'HDF' in data_type:
            os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
            from tensorflow.keras.models import load_model
            with h5py.File(target, 'r') as f:
                model = load_model(f)
            return model
        else:
            return None

        

    # def SendArray(self, request, context):
    #     print('train')
    #     target = deserialize(request.target_array)
    #     print(target)
    #     if target is not None:
    #         return numpy_test_pb2.CompleteReply(complete=1)
    #     else: return numpy_test_pb2.CompleteReply(complete=-1)

# def deserialize(target):
#     buf = BytesIO()
#     buf.write(target)
#     buf.seek(0)
#     data_type = buf.read()[:-3]
#     buf.seek(0)

#     if b'NUMPY' in data_type:
#         print('in')
#         return np.load(buf)
#     else: return -1

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_Data_Model_HandlerServicer_to_server(Data_model_handler(), server)
    server.add_insecure_port('[::]:8000')
    server.start()
    print('server start')
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()

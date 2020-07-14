import time
import logging
import grpc
import numpy as np
import h5py
from joblib import load, dump
from concurrent import futures
from io import BytesIO

import numpy_test_pb2
import numpy_test_pb2_grpc

class Data_model_handler(modi_ai_cloud_pb2_grpc.Data_Model_HandlerServicer):

    def SendObjects(self, request, context):
        train_data = __load_data(request.train_array)
        label_data = __load_data(request.label_array)
        model = __load_data(request.model)

        #TODO: training data by using given model

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

def deserialize(target):
    buf = BytesIO()
    buf.write(target)
    buf.seek(0)
    data_type = buf.read()[:-3]
    buf.seek(0)

    if b'NUMPY' in data_type:
        print('in')
        return np.load(buf)
    else: return -1

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    numpy_test_pb2_grpc.add_Train_Data_SenderServicer_to_server(Train_data_handler(), server)
    numpy_test_pb2_grpc.add_Label_Data_SenderServicer_to_server(Label_data_handler(), server)
    server.add_insecure_port('[::]:8000')
    server.start()
    print('server start')
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()

import socket
import threading
import time
import sys
import json
import os
import wave
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation, Dense, Dropout, Flatten, Conv2D, MaxPooling2D

from util.mlsocket import MLSocket
from sys import getsizeof

BUFFERSIZE = 2**10
FLAG_SIZE = 34

class MODI_cloud():
    
    def __init__(self, model, train_data, label_data):
        self.__reply = str()
        self.client_socket = None
        self.net_flag = threading.Event()
        self.host = 'ec2-15-164-216-238.ap-northeast-2.compute.amazonaws.com'
        self.port = 8000

        self.run(model, train_data, label_data)

    def run(self, model, train_data, label_data):
        print('hi')
        self.client_socket = MLSocket()
        print('hi2')
        self.client_socket.connect((self.host, self.port))

        # client = Client()

        # send_thread = threading.Thread(target=client.handle_send, args=(model, data))
        # send_thread.daemon = True
        # send_thread.start()
        self.handle_send(model, train_data, label_data)

        # self.net_flag.wait()

        # receive_thread = threading.Thread(target=client.handle_receive)
        # receive_thread.daemon = True
        # receive_thread.start()

        # receive_thread.join()
        # send_thread.join()

    
    def handle_receive(self):
        """ thread of receiving messages sent by server 
        """
        # while 1:
        try:
            self.__reply = client_socket.recv(BUFFERSIZE)
            print(self.__reply)
            # if self.__reply == 'completed': raise OSError
        except:
            print('disconnected')
            # break

        print('thread exit')

    def handle_send(self, model, train_data, label_data):
        """ thread of sending messages to server
        """
        
        # send model
        self.client_socket.sendall(model)
        
        # wait for receiving server's answer
        self.client_socket.recv(BUFFERSIZE)

        # send train data
        self.client_socket.sendall(train_data)

        # wait for receiving server's answer
        self.client_socket.recv(BUFFERSIZE).decode()

        # send label data
        self.client_socket.sendall(label_data)

        # wait for receiving server's answer
        tmp_str = self.client_socket.recv(BUFFERSIZE).decode()
        print(tmp_str)
        # self.net_flag.set()
            
        # client_socket.sendall(user.encode())
        # input('please press enter if you wanna send json file')
        # client_socket.sendall(meta_filename.encode())
        
        # # sending meta data
        # try:
        #     with open(meta_filename,'rb') as f:
        #         try:
        #             data = f.read(BUFFERSIZE)
        #             print(data)
        #             while data:
        #                 print('sending data')
        #                 client_socket.sendall(data)
        #                 data = f.read(1024)
        #         except Exception as e:
        #             print(e)
        # except:
        #     print('timeout. server noresponse')
        #     pass
        
        # print(label_list.keys())

        # for label in label_list.keys():
        #     label_path = os.path.join(project_path,label)
        #     for i in range(label_list[label]):
        #         print(i)
        #         file_name = label + str(i) + '.' + file_type
        #         file_path  = os.path.join(label_path,file_name)
                
        #         while 1:
        #             if self.__reply == 'ready':
        #                 print(self.__reply)
        #                 file_size = str(self.__get_file_size(file_path))
        #                 client_socket.sendall(file_size.encode())
        #                 break

        #         while 1:
        #             # print(self._reply)
        #             if self.__reply == 'send':
        #                 print(self.__reply)
        #                 self.__file_trasnfer(client_socket,file_path)
        #                 print('out')
        #                 break
        # while 1:
        #     if self.__reply == 'completed':
        #         client_socket.sendall('sendall'.encode())
        #         break
            
                
        # client_socket.close()
        
    def __get_file_size(self, filepath):

        return os.path.getsize(filepath)
        
    def __file_trasnfer(self, client_socket, file_path):
        print('file transfer')
        # TODO : 데이터 폼 별로 file handler가 따로 있어야 함
        with open(file_path,'rb') as f:
            try:
                data = f.read(BUFFERSIZE)
                while data:
                    client_socket.sendall(data)
                    data = f.read(BUFFERSIZE)
            except Exception as e:
                print('error')
                print(e,flush=True)
                pass
        
        """ sound file
        with wave.open(file_path,'rb') as w:
            try:
                data = w.readframes(BUFFERSIZE)
                while data:
                    client_socket.sendall(data)
                    data = w.readframes(BUFFERSIZE)
            except Exception as e:
                print('error')
                print(e,flush=True)
                pass
        """

if __name__ == "__main__":
    
    # Make an ndarray
    train_data = np.array([1, 2, 3, 4])
    label_data = np.array([4, 5, 6, 7])

    # Make a keras model
    model = Sequential()
    model.add(Dense(8, input_shape=(None, 4)))
    model.compile(optimizer='adam', loss='binary_crossentropy')

    # Make a scikit-learn classifier
    # clf = svm.SVC(gamma=0.00314)

    MODI_cloud(model, train_data, label_data)
    
    
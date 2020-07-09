import socket
import threading
import time
import sys
import json
import os
import wave

from sys import getsizeof

BUFFERSIZE = 2**10
FLAG_SIZE = 34
class Client():
    
    def __init__(self):
        self.__reply = str()

    def run(self):
        meta_filename = input('json filename : ')

        try:
            with open(meta_filename,'rb') as f:
                user_metadata = json.load(f)
        except:
            print('json load error')
            sys.exit()

        user_name = user_metadata['USER']
        host = user_metadata['HOST']
        port = user_metadata['PORT']
        work_space = user_metadata['WORK_SPACE']
        project_name = user_metadata['PROJECT_NAME']
        file_type = user_metadata['FILE_TYPE']
        project_path = os.path.join(work_space,project_name)
        label_list = user_metadata['LABELS']

        # with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client_socket:
        client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_socket.connect((host,port))

        client = Client()

        receive_thread = threading.Thread(target=client.handle_receive, args=(1,client_socket,user_name,project_path,label_list))
        receive_thread.daemon = True
        receive_thread.start()

        send_thread = threading.Thread(target=client.handle_send,args=(2,client_socket,user_name,meta_filename,project_path,file_type,label_list))
        send_thread.daemon = True
        send_thread.start()

        receive_thread.join()
        send_thread.join()

    
    def handle_receive(self,num,client_socket,user,project_path,label_list):
        """ thread of receiving messages sent by server 
        """
        while 1:
            try:
                self.__reply = client_socket.recv(BUFFERSIZE)
                self.__reply = self.__reply.decode()
                print(self.__reply)
    
                if self.__reply == 'completed': raise OSError
            except:
                print('disconnected')
                break

        print('thread exit')

    def handle_send(self,num,client_socket,user, meta_filename,project_path,file_type,label_list):
        """ thread of sending messages to server
        """
        
        client_socket.sendall(user.encode())
        input('please press enter if you wanna send json file')
        client_socket.sendall(meta_filename.encode())
        
        # sending meta data
        try:
            with open(meta_filename,'rb') as f:
                try:
                    data = f.read(BUFFERSIZE)
                    print(data)
                    while data:
                        print('sending data')
                        client_socket.sendall(data)
                        data = f.read(1024)
                except Exception as e:
                    print(e)
        except:
            print('timeout. server noresponse')
            pass
        
        print(label_list.keys())

        for label in label_list.keys():
            label_path = os.path.join(project_path,label)
            for i in range(label_list[label]):
                print(i)
                file_name = label + str(i) + '.' + file_type
                file_path  = os.path.join(label_path,file_name)
                
                while 1:
                    if self.__reply == 'ready':
                        print(self.__reply)
                        file_size = str(self.__get_file_size(file_path))
                        client_socket.sendall(file_size.encode())
                        break

                while 1:
                    # print(self._reply)
                    if self.__reply == 'send':
                        print(self.__reply)
                        self.__file_trasnfer(client_socket,file_path)
                        print('out')
                        break
        while 1:
            if self.__reply == 'completed':
                client_socket.sendall('sendall'.encode())
                break
            
                
        client_socket.close()
        
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
    
    client = Client()
    client.run()
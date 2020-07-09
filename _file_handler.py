import time
import queue
import json
import os
import wave
import threading

BUFFERSIZE = 2**10

class Handler():
    def __init__(self, user_dir,client_socket):
        
        self.__client_socket = client_socket

        self.__json_Filename = str()
        self.__json_metadata = {}
        self.__user_dir = user_dir
        self.__byteStream_recv_q = queue.Queue()
        self.__filename_list = []

        self.__raw_message_buffer = bytes()

    def write_meta_file(self):
        """ store Json_File
        """
        
        json_Filename = self.__client_socket.recv(BUFFERSIZE)
        print(json_Filename)
        self.__json_Filename = json_Filename.decode()

        with open(self.__user_dir + '\\metadata\\' + self.__json_Filename,'wb') as f:
            try:
                json_data = self.__client_socket.recv(BUFFERSIZE)
                print(json_data)
                while json_data:
                    f.write(json_data)
                    f.flush()
                    json_data = None
            except Exception as e:
                print('storing json error')
                print(e)
                return False
         
        return True     

    def parsing_meta_file(self):
        """ parsing Json file
        """
        with open(self.__user_dir+"\\metadata\\"+self.__json_Filename,'rb') as f:
            try:
                self.__json_metadata = json.load(f)
            except Exception as e:
                print('parsing json error')
                print(e)
                return None
        
        return self.__json_metadata

    def write(self,file_path,is_sendall=False):
        """ write file
        """
        if is_sendall:
            print('aaaaaa')
            self.__proc_training_file(filesize=0,file_path='',is_sendall=True)
            return

        self.__filename_list.append(file_path)
        self.__client_socket.sendall('ready'.encode())

        print('wait')
        filesize = int(self.__client_socket.recv(BUFFERSIZE).decode())

        if not filesize:
            print('send filesize')
            return
        
        # p_thread = threading.Thread(target=self.__proc_training_file,args=(filesize,file_path,False))
        # p_thread.daemon = True
        # p_thread.start()

        # w_thread = threading.Thread(target=self.write_training_file)
        # w_thread.daemon = True
        # w_thread.start()

        # p_thread.join()

        self.__proc_training_file(filesize,file_path,is_sendall)

    def __proc_training_file(self,filesize,file_path,is_sendall):
        """ process and insert chunk in Q
        """
        if is_sendall:
            print('bbbbb')
            self.__byteStream_recv_q.put('sendall'.encode())
            return

        self.__filename_list.append(file_path)
        self.__byteStream_recv_q.put('start'.encode())

        self.__client_socket.sendall('send'.encode())

        for i in range(filesize//BUFFERSIZE+1):
            data = self.__client_socket.recv(BUFFERSIZE)
            self.__byteStream_recv_q.put(data)
            
        self.__byteStream_recv_q.put('finish'.encode())
        
    def write_training_file(self):
        """ store training data set
        """
        while 1:
            data = self.__byteStream_recv_q.get()
            if data.decode() == 'start':
                with open(self.__filename_list.pop(),'wb') as f:
                    data = self.__byteStream_recv_q.get()
                    while 1:
                        f.write(data)
                        data = self.__byteStream_recv_q.get()

                        if data.decode() == 'finish': break
            
            if data.decode() == 'sendall':
                print('file transfer complete')
                break

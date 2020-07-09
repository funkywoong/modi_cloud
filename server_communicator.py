import socket
import threading
import time
import select
import multiprocessing  
import json
import sys
import os

from os.path import join
from mlsocket import MLSocket
from _file_handler import Handler
from _directory_handler import D_Handler
# import numpy as numpy

# from sklearn.datasets import fetch_openml

BUFFERSIZE = 2**10

class Server():
    """ managing communication with Clinets 
    """

    def __init__(self, port, host='', thread_Num=5):

        self.__stopped = False
        
        self.host = host
        self.port = port
        self.thread_Num = thread_Num
        self.user_list = {}
        self.input_list = []
        self.server_socket = None

        # creating socket object
        try:
            self.server_socket = MLSocket()
            # self.server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            # self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        # exception handling
        except Exception:
            print("socket creating error, please reboot the server")
            sys.exit()

        self.server_socket.bind((self.host,self.port))

        self.__accept_func()
        
    def __accept_func(self):
        """ accept client request and handle it
        """
        
        # start listening
        print("server activate")
        
        # self.server_socket.listen(self.thread_Num)
        self.server_socket.listen()
        input_list = [self.server_socket]

        while 1:
            try:
                input_ready, _, _ = select.select(input_list,[],[])

                for conn_read_socket in input_ready:
                    print(conn_read_socket)

                    #check sys.stdin in UNIX/LINUX
                    """
                    if ir == sys.stdin:
                        junk = sys.stdin.readline()
                        print(junk,flush = True)
                    """
                    
                    if isinstance(conn_read_socket, self,server_socket):
                    # if conn_read_socket is self.server_socket:
                        try:
                            client_socket, addr = self.server_socket.accept()
                            # user = client_socket.recv(BUFFERSIZE)
                            # print(addr," is connected, user = ",user.decode(),flush=True)
                            
                            #append connected used
                            input_list.append(client_socket)
                            # self.user_list[user] = client_socket
                        except Exception as e:
                            print(e)
                            pass
                        finally:
                            receive_thread = threading.Thread(target=self.__handle_receive, args=(self.user_list[user],addr,user,input_list))
                            receive_thread.daemon = True
                            receive_thread.start()
            except KeyboardInterrupt:
                #close all information
                for _, each_connect in self.user_list:
                    each_connect.close()
                print("Keyboard interrupt",flush=True)
                self.__close_func()

                break
            except Exception as e:
                print(e)
                break

    def __handle_receive(self,client_socket,addr,user,input_list):
        """ thread of each client task
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))
        user_dir = join(base_dir,user.decode())

        dir_handler = D_Handler()

        # create user own space if new
        if dir_handler.is_New_User(base_dir,user_dir):
            dir_handler.make_User_Space(user_dir)

        # initialize user file handler
        handler = Handler(user_dir,client_socket)
        
        try:
            # receive and store json metadata filename (user_dir/metadata)
            if not handler.write_meta_file():
                raise IOError

            # parsing json format
            metadata = handler.parsing_meta_file()
            if not metadata:
                raise IOError
            
            # create project space if new
            project_dir = join(user_dir,metadata['PROJECT_NAME'])
            if dir_handler.is_New_Project(user_dir,project_dir):
                dir_handler.make_Project_Space(project_dir)

            # create label space if new
            label_list = metadata['LABELS']

            write_daemon = threading.Thread(target=handler.write_training_file)
            write_daemon.daemon = True
            write_daemon.start()

            # receive training data
            for label in label_list.keys():
                label_dir = join(project_dir,label)
                if dir_handler.is_New_Label(project_dir,label_dir):
                    dir_handler.make_Label_Space(label_dir)

                for i in range(label_list[label]):
                    file_name = label + str(i) + '.' + metadata['FILE_TYPE']
                    file_path = join(label_dir,file_name)
                    print(i)
                    handler.write(file_path)

            client_socket.sendall('completed'.encode())

            is_sendall = client_socket.recv(BUFFERSIZE)

            if is_sendall.decode() == 'sendall':
                handler.write(file_path=None,is_sendall=True)

            # write_daemon.join()

        except Exception as e:
            print(e)

        # remove all information of disconnected client
        del self.user_list[user]
        input_list.remove(client_socket)

        client_socket.close()

        print('thread exit')
  
    def __is_New_User(self,base_dir,user_dir):
        """ is new user?
        """
        if user_dir not in os.listdir(base_dir):
            return True

        return False

    def __make_User_Space(self,user_dir):
        """ make user directory on Server
        """
        try:
            os.makedirs(user_dir)
            os.makedirs(user_dir+'\\metadata')

        except:
            print('User already exists')
            pass

    def __is_New_Project(self,user_dir,project_dir):
        """ is new project?
        """
        if project_dir not in os.listdir(user_dir):
            return True
        
        return False

    def __make_Project_Space(self,project_dir):
        """ make project directory on Server
        """
        try:
            os.makedirs(project_dir)
        except:
            print('Project already exists')
            pass

    def __is_New_Label(self,project_dir,label_dir):
        """ is new label?
        """

        if label_dir not in os.listdir(project_dir):
            return True
        
        return False

    def __make_Label_Space(self,label_dir):
        """ make label directory on server
        """
        try:
            os.makedirs(label_dir)
        except:
            print('Label already exists')
            pass

    def __close_func(self):
        """ close server socket
        """
        self.server_socket.close()

if __name__ == "__main__":

    server = Server(host='',port =8000)
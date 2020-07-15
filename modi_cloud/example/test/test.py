import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import utils
from tensorflow.keras import layers
from tensorflow.keras import datasets
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Activation, Dense, Dropout, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing import image
from sklearn.model_selection import train_test_split
# from image_augmentation import imgdatagen

import numpy as np
import matplotlib.pyplot as plt
import os

def gen_data():
    train_img_src_list = []

    # 학습 이미지 라벨링
    class_names = [
        'car3_person',
        'car3_red',
        'car3_unknown'
    ]
    data_directory = 'example/test/new_car3_data'

    # train data list, label list 생성
    X_ = []
    y_ = []

    fig = plt.figure()
    rows = 100
    cols = 6
    i = 1

    # 데이터별 path 설정
    for label_idx, target in enumerate(class_names):
            
        target_directory = data_directory + '/' + target
        label_cnt = len(os.listdir(data_directory))    
        test_cnt = 0
        
        print(target_directory)
        
        for each_file in os.listdir(target_directory):
            
            test_cnt += 1
            
            # 각 train image 파일 path 설정
            file_path = '{}/{}/{}'.format(data_directory, target, each_file)
            # train image file load
            tmp_img = image.load_img(file_path, target_size = (240, 320))
            # convert images to numpy array
            tmp_img = image.img_to_array(tmp_img)
            # normalization (1e-8 -> 분모가 0이 되는 것을 방지하기 위한 매우 작은 상수)
            tmp_img = tmp_img / 255.

            # Width x Height x RGB 에 해당하는 3차원 numpy 배열을 flattening
            X_.append(tmp_img)
            
            # one-hot encoding(labeling)
            temp_label = np.repeat(0, label_cnt)
            temp_label[label_idx] = 1
            y_.append(temp_label)
            
            if test_cnt == 1000: break
            
    X_ = np.array(X_).astype(np.float16)
    y_ = np.array(y_).astype(np.float16)
            
    # train, test data set split
    X_train, X_temp, y_train, y_temp = train_test_split(X_, y_, test_size = 0.6, random_state = 100)
    X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size = 0.5, random_state = 100)

    print(X_train.shape)
    print(X_valid.shape)
    print(X_test.shape)
    print(y_train.shape)
    print(y_valid.shape)
    print(y_test.shape)

    return X_train, X_valid, X_test, y_train, y_valid, y_test

def gen_model():

    # test case 1 padding = 'vaild'로 유효한 영역만 출력
    model = Sequential()
    model.add(
        Conv2D(input_shape = (240, 320, 3), filters = 16, kernel_size = (3,3), strides = (3,3), 
            padding = 'same', activation = 'relu')
    )
    model.add(MaxPooling2D(pool_size = (2,2)))
    model.add(Dropout(0.25))

    model.add(
        Conv2D(filters = 64, kernel_size = (3,3), strides = (1,1), 
            padding = 'same', activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2,2)))
    model.add(Dropout(0.25))

    model.add(
        Conv2D(filters = 64, kernel_size = (3,3), strides = (1,1), 
            padding = 'same', activation = 'relu'))
    model.add(MaxPooling2D(pool_size = (2,2)))
    model.add(Dropout(0.25))

    print(model.output_shape)

    model.add(Flatten())
    # model.add(Dense(256, activation = 'relu'))
    model.add(Dropout(0.25))
    model.add(Dense(3, activation = 'softmax'))

    # model.add(Flatten())
    # model.add(Dense(256, activation = 'relu'))
    # model.add(Dropout(0.25))
    # model.add(Dense(6, activation = 'relu'))

    opt = keras.optimizers.Adam(learning_rate = 0.001)
    model.compile(loss = 'categorical_crossentropy', optimizer = opt, metrics = ['accuracy',])

    return model
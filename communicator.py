
import json

import numpy as np

from sklearn.datasets import fetch_openml


class Communicator:
    """Receive and send data
    """

    def __init__(self):
        pass

    def recv_metadata(self, mock=False):
        # TODO: remove this mock meta data generation
        if mock:
            # creating mock json data for numerical data
            mock_data = {}
            mock_data['train'] = 'yes'
            mock_data['data_type'] = 'image'
            
            # preprocessor
            mock_data['preprocessors'] = 'normalize,grey_scale'

            # model
            mock_data['models'] = 'randomforest,svm'
        
        return json.dumps(mock_data)

    def recv_data(self):
        # creating mock dataset
        mnist = fetch_openml('mnist_784')
        return mnist.data, mnist.target

    # TODO: send_data vs send_model vs send_models, model vs models?
    def send_models(self, models):
        print('sending models:', models)


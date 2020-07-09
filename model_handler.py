
import os
import pickle

# machine learning models
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC

# deep learning models
import torchvision.models as pytorch_models


class ModelHandler:
    ml_model_names = ['randomforest', 'svm']
    #dl_model_names = ['mobilenet']

    def __init__(self, model_names_str):
        model_names = model_names_str.replace(' ', '').split(',')
        self.models = self.__init_models(model_names)

    def train(self, X, y):
        for model_name, model in self.models.items():
            print(f'Start training {model_name}')
            eval(f'{model}.fit(X, y)')

    def save_models(self, dirpath='models'):
        for model_name, model in self.models.items():
            model_path = os.path.join(dirpath, model_name) + '.pkl'
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
        return self.models.keys()

    # private methods
    def __init_models(self, model_names):
        models = {}
        for model_name in model_names:
            print('curr model:' + model_name)
            curr_model = self.__init_model(model_name)
            models[model_name] = curr_model
        return models

    def __init_model(self, model_name):
        model = None
        if model_name in self.ml_model_names:
            model = self.__init_ml_model(model_name)
        else:
            model = self.__init_dl_model(model_name)
        return model

    def __init_ml_model(self, ml_model_name):
        ml_model = {
            'randomforest' : RandomForestClassifier(),
            'svm' : SVC(kernel='linear'),
        }.get(ml_model_name)
        return ml_model

    def __init_dl_model(self, dl_model_name):
        dl_model = {
            #'vgg16' : pytorch_models.vgg16(),
            #'vgg19' : pytorch_models.vgg19(),
            'mobilenet' : pytorch_models.mobilenet_v2(),
        }.get(dl_model_name)
        return dl_model


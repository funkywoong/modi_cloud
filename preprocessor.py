
import numpy as np


class Preprocessor:

    def __init__(self, X, y):
        self.X = X
        self.y = y

    def preprocess(self, preprocessing_methods_str):
        assert type(preprocessing_methods_str) is str

        preprocessing_methods = \
                preprocessing_methods_str.replace(' ', '').split(',')
        for preprocessing_method in preprocessing_methods:
            eval(f'self.{preprocessing_method}()')
        return self.X, self.y

    def normalize(self):
        pass

    def cross_validate(self):
        pass


class NumberPreprocessor(Preprocessor):

    def __init__(self, X, y):
        super().__init__(X, y)

    def remove_outlier(self):
        pass


class ImagePreprocessor(Preprocessor):

    def __init__(self, X, y):
        super().__init__(X, y)

    def grey_scale(self):
        pass


class SpeechPreprocessor(Preprocessor):

    def __init__(self, X, y):
        super().__init__(X, y)


class TextPreprocessor(Preprocessor):

    def __init__(self, X, y):
        super().__init__(X, y)


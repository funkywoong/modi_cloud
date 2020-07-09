
import json

from pprint import pprint

from communicator import Communicator

from preprocessor import NumberPreprocessor
from preprocessor import ImagePreprocessor
from preprocessor import SpeechPreprocessor
from preprocessor import TextPreprocessor

from model_handler import ModelHandler


def allocate_preprocessor(data_type):
    preprocessor = {
        'number' : NumberPreprocessor,
        'image' : ImagePreprocessor,
        'speech' : SpeechPreprocessor,
        'text' : TextPreprocessor,
    }.get(data_type)
    return preprocessor


def main():
    # init communicator which communicates with modi-studio
    c = Communicator()

    # receives training data
    metadata = json.loads(c.recv_metadata(mock=True))

    # reveal training data type
    data_type = metadata['data_type']

    # allocate preprocessor accordingly
    typed_preprocessor = allocate_preprocessor(data_type)

    # initialize preprocessor
    X, y = c.recv_data()
    preproc_inst = typed_preprocessor(X, y)

    # preprocess the data as user requested
    requested_preprocessing_methods = metadata['preprocessors']
    X, y = preproc_inst.preprocess(requested_preprocessing_methods)

    # get learning model(s) of user choice (e.g. NN, RF etc.)
    requested_learning_models = metadata['models']
    model_handler = ModelHandler(requested_learning_models)

    # train models with the collected data
    model_handler.train(X[:100], y[:100])

    # save the trained models locally
    models = model_handler.save_models()
    
    # send the trained models to modi-studio?
    c.send_models(models)


if __name__ == '__main__':
    main()


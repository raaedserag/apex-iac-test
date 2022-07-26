import pickle
import json
import os
from io import BytesIO

from azureml.core.model import Model
from azureml.core import Workspace, Dataset
from azure.identity import DefaultAzureCredential
from azureml.monitoring import ModelDataCollector
from azure.storage.blob import BlobServiceClient

import numpy as np
import pandas as pd
import ktrain
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


#MODEL_NAME = "distilbert-base-uncased"
#STORAGE_ACCOUNT_NAME = "rprclncadls01dev"
#SM_CONTAINER = "inferencedata"
#SM_BLOB = "RC_HelpSymptomDescriptions.csv"

def load_symptom_mappings():
    """Load Symptom mappings file

    Load data from blob storage that contains the symptom mappings
    """
    my_storage_account_url = "https://{}.blob.core.windows.net/".format(os.getenv('STORAGE_ACCOUNT_NAME'))

    # This will use your Azure Managed Identity
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=my_storage_account_url,
        credential=credential
    )
    blob_client = blob_service_client.get_blob_client(container=os.getenv('SM_CONTAINER'), blob=os.getenv('SM_BLOB'))
    blob_data = blob_client.download_blob()

    return pd.read_csv(BytesIO(blob_data.readall()),sep=",")


def init():
    """Init gets called at start of service

    Consider this a startup script section
    """
    global reloaded_predictor
    global porter
    global symptom_mappings
    global stop_words

    # Load the model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), os.getenv('MODEL_NAME'))
    reloaded_predictor = ktrain.load_predictor(model_path)

    # Load the symptom id mapping dataset
    symptom_mappings = load_symptom_mappings()

    # Load preprocessing and stop words
    porter = PorterStemmer()
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

    # Loading data collection
    global inputs_dc, prediction_dc
    inputs_dc = ModelDataCollector(os.getenv('MODEL_NAME'), designation="inputs", feature_names=["text"])
    prediction_dc = ModelDataCollector(os.getenv('MODEL_NAME'), designation="predictions", feature_names=["symptom", "symptom_id", "probability"])


def remove_punctuation_numbers(sentence):
    symbols = "1234567890!\"#$%&()*+-./:;<=>?@[\]^_`{|}~\n"
    for i in symbols:
        sentence = sentence.replace(i, ' ')
    return sentence


def remove_single_characters(sentence):
    words = sentence.split()
    new_text = ""
    for w in words:
        if len(w) > 1:
            new_text = new_text + " " + w
    return new_text


def remove_stop_words(sentence):
    words = sentence.split()
    new_text = ""
    for word in words:
        if word not in stop_words:
            new_text += " " + word

    return new_text


def stem(sentence):
    words = sentence.split()
    new_text = ""
    for word in words:
        w = porter.stem(word)
        new_text = new_text + " " + w
    return new_text


def preprocess(i):
    i = i.lower()
    i = remove_punctuation_numbers(i)
    i = remove_single_characters(i)
    i = remove_stop_words(i)
    i = stem(i)
    i = remove_punctuation_numbers(i)
    return i


def get_predictions_probs(text, predictor, appliance = False, n = 5):
    """Method designed to take in new raw text and a predictor in the form of a ktrain model predictor.
    and return an array of tuples containing symptoms and their associated probabilities.
    
    Parameters
    ----------------------------------------------------------------
    
    text: string-like.
        Text whose symptom is to be predicted
    
    predictor: ktrain load_predictor() object
        Ktrain object for making predcitions based on a loaded model and an input text.
        In this instance the 'return_proba' parameter will always be used, meaning that the return of this call
        will always be a numpy array of floats (probabilities) of the size of the list of classes to be predicted.
        
    n : int or none, optional
        The top n predictions that the model will return. Default = 5
        """

    classes =  predictor.get_classes()
    probs = predictor.predict([text], return_proba=True)[0][:].tolist()
    
    if appliance != False:
        inds = [i for i, ele in enumerate(predictor.get_classes()) if appliance in ele]
        if len(inds) > 0:
            classes = np.array(classes)[inds]
            probs = np.array(probs)[inds]
            probs = [float(prob)/sum(probs) for prob in probs]
    
    dtype = [('class', 'U500'), ('probability', float)]
    data = []
    
    for i in range (0,len(classes)):
        data.append((classes[i], np.round(probs[i], 3)))

    result = np.array(data, dtype=dtype) 
    result = np.sort(result, order = 'probability')
        
    return np.flip(result)[:n]


def get_predictions_probs_w_id(text, predictor, appliance = False, n = 5):
    cleaned_text = preprocess(text)
    result = get_predictions_probs(cleaned_text, predictor, appliance = False, n = 5)
    new_result = []
    for item in result:
        for id in symptom_mappings[symptom_mappings['SymptomDescription'] == item[0]]['HelpSymptom_ID']:
            item_result = {
                'symptom': item[0],
                'symptom_id': int(id),
                'probability': item[1]
            }
            new_result.append(item_result)

    response_str = {
        'input_text': text,
        'symptom_results': new_result
    }
    return response_str


def data_collection(input, result):
    """Collect data for monitoring"""
    correlations = inputs_dc.collect([input])
    predictions_data = pd.DataFrame(result['symptom_results'])
    predictions_data['input_text'] = input
    predictions_data = prediction_dc.add_correlations(predictions_data, correlations)
    prediction_dc.collect(predictions_data)


def run(rawdata):
    try:
        data = json.loads(rawdata)
        result = get_predictions_probs_w_id(data['text'], reloaded_predictor)

        data_collection(data['text'], result)

        return json.dumps(result)
    except Exception as e:
        result = str(e)
        return json.dumps({"error": result})

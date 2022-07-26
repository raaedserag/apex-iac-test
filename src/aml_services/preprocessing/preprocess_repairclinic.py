import argparse
import os
import pandas as pd
import numpy as np
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from azureml.core import Dataset, Run

print("In preprocess.py")

parser = argparse.ArgumentParser("preprocess")
parser.add_argument("--input", type=str, help="input raw data")
parser.add_argument("--output", type=str, help="output directory for processed data")

args = parser.parse_args()

print("Argument 1: %s" % args.input)
print("Argument 2: %s" % args.output)

# Define helper function
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
    stop_words = set(stopwords.words('english'))
    words = sentence.split()
    new_text = ""
    for word in words:
        if word not in stop_words:
            new_text += " " + word
    return new_text

def stem(sentence):
    porter = PorterStemmer()
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

def remove_none_one(df):
    filtered_df = df.copy()
    dictionary = dict(df['SYMPTOM'].value_counts())
    only_one_example = []
    for key in dictionary:
        if dictionary[key] == 1:
            only_one_example.append(key)
    for i in only_one_example:
        filtered_df = filtered_df[filtered_df['SYMPTOM'] != i]
    return filtered_df

# main preprocess function
def clean_training_data(df):
    clean_df = df.copy()
    clean_df['CUSTOMER_COMPLAINT_PREPROCESSED'] = clean_df['CUSTOMER_COMPLAINT'].apply(preprocess)
    clean_df = clean_df[~clean_df['SYMPTOM'].isin(['nan', 'na', None, np.NaN])]
    clean_plus_one_df = remove_none_one(clean_df)
    return clean_plus_one_df

#Input as dataset
run = Run.get_context()
ws = run.experiment.workspace

# get the input dataset by ID
dataset = Dataset.get_by_name(ws, name=args.input)

# load the TabularDataset to pandas DataFrame
data = dataset.to_pandas_dataframe()

train_df = clean_training_data(data)

print('Preprocessing data done!')

if not (args.output is None):
    os.makedirs(args.output, exist_ok=True)
    # Save the features and output values
    train_df.to_csv(os.path.join(args.output, "processed-data.csv"), header=True, index=False)
    print('Processed data file saved!')
    
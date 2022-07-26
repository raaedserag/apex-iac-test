import argparse
import os
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from azureml.core import Dataset, Run

from utils.event import send_event

######## Define Statics ############################

EVENT_TYPE="BAPG.ML.REPAIRCLINIC.DRIFT"
SUBJECT="Repair Clinic model drift event"
DATA_VERSION="1.0"
METRIC="input_data_drift"

#####################################################


def compute_cosine_similarity(doc1, doc2):
    documents = [doc1, doc2]
    count_vectorizer = CountVectorizer(stop_words='english')
    count_vectorizer = CountVectorizer()
    sparse_matrix = count_vectorizer.fit_transform(documents)

    doc_term_matrix = sparse_matrix.todense()
    df = pd.DataFrame(doc_term_matrix, 
                  columns=count_vectorizer.get_feature_names(), 
                  index=['doc1', 'doc'])
    return cosine_similarity(df, df)


def main():
    print("In cosine_similarity.py")

    ######## Parse Arguments ############################
    parser = argparse.ArgumentParser("cosine_similarity")
    parser.add_argument("--input1", type=str, help="traing input data")
    parser.add_argument("--input2", type=str, help="inference input data")
    parser.add_argument("--drift_threshold", type=float, help="drift metric threshold")
    parser.add_argument("--event_endpoint", type=str, help="event endpoint")
    parser.add_argument("--output", type=str, help="calculated drift data")

    args = parser.parse_args()

    print("Argument 1: %s" % args.input1)
    print("Argument 2: %s" % args.input2)
    print("Argument 3: %s" % args.drift_threshold)
    print("Argument 4: %s" % args.event_endpoint)
    print("Argument 5: %s" % args.output)
    ######################################################

    ######## Load Context and Data #######################
    run = Run.get_context()
    ws = run.experiment.workspace

    # get the input dataset by ID
    data1 = Dataset.get_by_id(ws, id=args.input1)
    data2 = Dataset.get_by_id(ws, id=args.input2)

    # load the TabularDataset to pandas DataFrame
    df1 = data1.to_pandas_dataframe()
    df2 = data2.to_pandas_dataframe()
    ######################################################

    ######## Perform Calculations ########################
    # def convert_feature_to_doc(data):
    #     text_list = data['CUSTOMER_COMPLAINT'].tolist()
    #     doc = ''.join(text_list)
    #     return doc
    text_list1 = df1['CUSTOMER_COMPLAINT'].tolist()
    doc1 = ''.join(text_list1)
    text_list2 = df2['text'].tolist()
    doc2 = ''.join(text_list2)

    drift_metrics = compute_cosine_similarity(doc1, doc2)[0][1]

    print('Cosine Similarity: %s' % drift_metrics)

    # Send an event with the calculated drift metrics
    send_event(data={METRIC, drift_metrics},
                subject=SUBJECT,
                event_type=EVENT_TYPE,
                data_version=DATA_VERSION,
                endpoint=args.event_endpoint)

    if drift_metrics > args.drift_threshold:
        alert = 'Drift NOT Detected'
        print('Data drift NOT detected!')
    else:
        alert = 'Drift Detected'
        print('Data drift detected!')

    if not (args.output is None):
        os.makedirs(args.output, exist_ok=True)
        # Save the features and output values
        pd.DataFrame([alert]).to_csv(os.path.join(args.output, "alert.csv"), header=['alert'], index=False)
        print('Alert message file saved!')


if __name__ == '__main__':
    main()
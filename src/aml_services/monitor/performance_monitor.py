import argparse
import os
import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency

from azureml.core import Dataset, Run

from utils.event import send_event

######## Define Statics ############################

EVENT_TYPE="BAPG.ML.REPAIRCLINIC.DRIFT"
SUBJECT="Repair Clinic model performance drift event"
DATA_VERSION="1.0"
METRIC="performance_drift"

#####################################################

def compute_baseline_proportions(training_df):
    total_training_rows = training_df['SYMPTOM'].value_counts().sum()
    training_response_dist_df = training_df['SYMPTOM'].value_counts().reset_index()
    training_response_dist_df = training_response_dist_df.rename(columns={'index': 'Symptom', 'SYMPTOM': 'Baseline_Count'})
    training_response_dist_df['Proportion'] = training_response_dist_df['Baseline_Count'] / total_training_rows
    return training_response_dist_df


def compute_target_expectations(input_df, proportion_df, target_len):
    target_df = input_df.copy()
    target_df = target_df.merge(proportion_df, how='outer', on='Symptom')
    target_df['Expected_Count'] = target_df['Proportion'] * target_len
    target_df = target_df.drop(columns=['Baseline_Count', 'Proportion'])
    target_df = target_df.fillna(0)
    return target_df


def perform_chi2(comparision_df, expected_col, target_col):
    c, p, df, expected = chi2_contingency(comparision_df[[expected_col, target_col]].to_numpy())
    print(p, df)
    # real hurdle here
    # drift_threshold = 0.05
    # fake hurdle here
    return p


def main():
    print("In chi_square.py")

    ######## Parse Arguments ############################
    parser = argparse.ArgumentParser("chi_square")
    parser.add_argument("--input1", type=str, help="training input data")
    parser.add_argument("--drift_threshold", type=float, help="drift metric threshold")
    parser.add_argument("--event_endpoint", type=str, help="event endpoint")
    # parser.add_argument("--input2", type=str, help="inference prediction data")
    parser.add_argument("--output", type=str, help="calculated drift data")

    args = parser.parse_args()

    print("Input 1: %s" % args.input1)
    print("Drift Threshold: %s" % args.drift_threshold)
    print("Event Endpoit: %s" % args.event_endpoint)
    # print("Argument 2: %s" % args.input2)
    print("Output: %s" % args.output)
    ######################################################

    ######## Load Context and Data #######################
    run = Run.get_context()
    ws = run.experiment.workspace

    # get the input dataset by ID
    data1 = Dataset.get_by_id(ws, id=args.input1)
    # data2 = Dataset.get_by_id(ws, id=args.input2)

    # load the TabularDataset to pandas DataFrame
    training_df = data1.to_pandas_dataframe()
    # df2 = data2.to_pandas_dataframe()
    ######################################################

    ######## Perform Calculations ########################
    # Simulates Collected Prediction Data
    # Just need top predicted symptom from responses.
    # Need Responses with following columns:  'Symptom', 'Target_Count'
    baseline_df = compute_baseline_proportions(training_df)

    target_len = 300
    target_df = training_df.sample(n=target_len)['SYMPTOM'].value_counts().reset_index().rename(columns={'index': 'Symptom', 'SYMPTOM': 'Target_Count'})
    comparision_df = compute_target_expectations(target_df, baseline_df, target_len)
    perf_metric = perform_chi2(comparision_df, 'Expected_Count', 'Target_Count')

    if perf_metric < args.drift_threshold:
        alert = 'Drift Detected'
        print("ALERT: Significant difference exists")
    else:
        alert = 'Drift NOT Detected'
        print("No significant difference exists")

    # Send notification of drift run metrics
    send_event(data={METRIC, perf_metric},
            subject=SUBJECT,
            event_type=EVENT_TYPE,
            data_version=DATA_VERSION,
            endpoint=args.event_endpoint)

    if not (args.output is None):
        os.makedirs(args.output, exist_ok=True)
        # Save the features and output values
        pd.DataFrame([alert]).to_csv(os.path.join(args.output, "alert.csv"), header=['alert'], index=False)
        print('Alert message file saved!')

if __name__ == '__main__':
    main()

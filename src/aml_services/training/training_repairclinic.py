
import azureml.dataprep as dprep
import joblib
import ktrain
from ktrain import text
import os
import numpy as np
from sklearn.model_selection import train_test_split

top_list_of_symptoms = [ "Washer won't spin"
        , "Washer is making loud noise"
        , "Washer won't spin or agitate"
        , "Washer won't agitate"
        , "Washer won't start"
        , "Oven temperature not accurate"
        , "Oven not heating"
        , "Oven won't turn on"
        , "Oven broiler not working"
        , "Washer overflowing"
        , "Washer door or lid won't lock"
        , "Oven doesn't bake evenly"
        , "Washer won't drain"
        , "Washer leaking water"
        , "Oven won't turn off"
        , "Washer stops mid cycle"
        , "Washer vibrating or shaking"
        , "Dryer won't start"
        , "Refrigerator is noisy or loud"
        , "Dryer makes noise"
        , "Dryer drum not turning"
        , "Oven light is out"
        , "Dryer stopped spinning"
        , "Washer fills slowly or will not fill at all"
        , "Dishwasher not draining"
        , "Dryer tripping breaker"
        , "Microwave shuts off after a few seconds"
        , "Refrigerator light not working"
        , "Refrigerator not cooling"
        , "Dryer won't stop"
        , "Dryer overheating"
        , "Microwave door won't open"
        , "Dryer not heating"
        , "Dryer takes too long"
        , "Dishwasher runs for several hours"
        , "Microwave not heating"
        , "Dishwasher won't start"
        , "Oven not self-cleaning"
        , "Refrigerator runs constantly"
        , "Refrigerator freezing food"
        , "Oven fan won't turn off"
        , "Microwave light bulb not working"
        , "Refrigerator ice and water dispenser not working"
        , "Refrigerator ice maker not working"
        , "Refrigerator water dispenser not working"
        , "Dishwasher lights flashing or blinking"
        , "Refrigerator freezer is cold but refrigerator is warm"
        , "Refrigerator not defrosting"
        , "Dishwasher won't latch"
        , "Refrigerator leaking water"
        , "Dishwasher not drying dishes"
        , "Microwave not working"
        , "Dishwasher leaking"
        , "Microwave turntable not turning"
        , "Dishwasher buttons not working"
        , "Microwave buttons not working"
        , "Dishwasher dispenser not dispensing soap"
        , "Stove burner won't light"
        , "Dishwasher leaking from motor area"
        , "Dishwasher making noise"
        , "Microwave display not working"
        , "Microwave turns on by itself"
        , "Oven door repair"
        , "Dishwasher not cleaning"
        , "Dishwasher overflowing"
        , "Dishwasher won't fill"
        , "Refrigerator ice maker overflowing"
        , "Range surface element won't turn off"
        , "Stove heating element not working"
        , "Microwave is sparking or arcing"
        , "Microwave is loud or noisy"
        , "Range burners spark all the time"
        , "Refrigerator ice dispenser not working"
        , "Refrigerator defrost drain clogged"
    ]

print("In train.py")

parser = argparse.ArgumentParser("train")
parser.add_argument("--input", type=str, help="processed_train_data")
parser.add_argument("--output", type=str, help="trained_model")

args = parser.parse_args()

print("Argument 1: %s" % args.input)
print("Argument 2: %s" % args.output)

# def train_model(train_df):
#     model_name = 'distilbert-base-uncased'
#     # training_df =  train_df.copy()
#     # print(training_df.columns)
#     X = np.array(training_df["CUSTOMER_COMPLAINT_PREPROCESSED"].tolist())
#     y = np.array(training_df["SYMPTOM"].tolist())
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1, stratify=y)
#     lr = 5e-5
#     lr_max = 5
#     t = text.Transformer(model_name, maxlen=500, class_names=top_list_of_symptoms)
#     trn = t.preprocess_train(X_train, y_train)
#     val = t.preprocess_test(X_test, y_test)
#     model = t.get_classifier()
#     learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=6)
#     learner.fit_onecycle(lr, lr_max)
#     return learner, y_test

def main():
    print("Running train.py")

    # Load the training data as dataframe
    # train_df = pd.read_csv(args.input)
    # train_df = args.input
    
    # Load pipeline data (file in this case) into a dataframe
    train_df = dprep.read_csv(path = args.input, infer_column_types = True).to_pandas_dataframe()
    
    # Train the model
    # model = train_model(train_df)
    model_name = 'distilbert-base-uncased'
    training_df =  train_df.copy()
    print(training_df.columns)
    X = np.array(training_df["CUSTOMER_COMPLAINT_PREPROCESSED"].tolist())
    y = np.array(training_df["SYMPTOM"].tolist())
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1, stratify=y)
    # lr = 5e-5
    # lr_max = 5
    t = text.Transformer(model_name, maxlen=500, class_names=top_list_of_symptoms)
    trn = t.preprocess_train(X_train, y_train)
    val = t.preprocess_test(X_test, y_test)
    model = t.get_classifier()
    learner = ktrain.get_learner(model, train_data=trn, val_data=val, batch_size=6)
    learner.fit_onecycle(5e-5, 1)

    # Evaluate and log the metrics returned from the train function
    # metrics = get_model_metrics(model, data)
    # for (k, v) in metrics.items():
    #     run.log(k, v)
    #     run.parent.log(k, v)
    learner.validate(class_names=list(set(y_test)))
    trn_accuracy = learner.history.history["accuracy"][-1]
    val_accuracy = learner.history.history["val_accuracy"][-1]

    # Conditional check on metrics to register the model
    hurdle_accuracy = 0.05
    if val_accuracy > hurdle_accuracy:
        print("Model accuracy is greater than hurdle accuracy")
        # good model, register it
        # Also upload model file to run outputs for history
        os.makedirs(args.output, exist_ok=True)
        output_path = os.path.join(args.output, model_name)
        # joblib.dump(value=learner, filename=output_path)
        predictor = ktrain.get_predictor(learner.model, t)
        predictor.save(output_path)
        # learner.save(output_path)
    else:
        print("Model accuracy is less than hurdle accuracy")
        # bad model, don't register it

    # Pass model file to next step
    # os.makedirs(args.step_output_path, exist_ok=True)
    # model_output_path = os.path.join(args.step_output_path, model_name)
    # joblib.dump(value=model, filename=model_output_path)

    # # Also upload model file to run outputs for history
    # os.makedirs(args.output, exist_ok=True)
    # output_path = os.path.join(args.output, model_name)
    # # joblib.dump(value=learner, filename=output_path)
    # predictor = ktrain.get_predictor(learner.model, t)
    # predictor.save(model_path)
    # # learner.save(output_path)

if __name__ == '__main__':
    main()

    # def validate_model(self):
    #     self.learner.validate(class_names=list(set(self.y_test)))
    #
    # def save_model(self):
    #     output_dir = os.path.join(self.__here__, 'outputs')
    #     os.makedirs(output_dir, exist_ok=True)
    #     model_path = os.path.join(output_dir, MODEL_PATH_PREFIX)
    #     predictor = ktrain.get_predictor(self.learner.model, self.t)
    #     predictor.save(model_path)
    #     self.model_path = model_path
    #
    #
    # def register_model(self):
    #     self.run.upload_folder(self.model_path, "outputs/" + MODEL_PATH_PREFIX)
    #     model = self.run.register_model(
    #         model_name=MODEL_NAME,
    #         model_path="outputs/" + MODEL_PATH_PREFIX
    #     )
    #     self.run.log('Model_ID', model.id)

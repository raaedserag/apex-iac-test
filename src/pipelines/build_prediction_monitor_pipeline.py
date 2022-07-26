from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core import Workspace, Dataset, Datastore
from azureml.core.runconfig import RunConfiguration
from azureml.data.data_reference import DataReference
from pipelines.load_sample_data import create_sample_data_csv
from aml_services.utils.attach_compute import get_compute
from aml_services.utils.env_variables import Env
from aml_services.utils.manage_environment import get_environment
from azureml.core import Experiment
import os


# data_location = 'aml-training-data'
# #This seems unused, since the train data is split in the train portion
# #test_data_location = 'aml-pipelines-test-data'


# #Unsure what this is for
# data_reference_name = 'repair_clinic_raw_data_3'
# #feature_data used as reference to blob story location 
# #feature_data = 'repair_clinic_raw_data_3/test_pipeline_symptom_predictor_raw_training.csv'


# feature_data = 'test_pipeline_symptom_predictor_raw_training.csv'


def main():
    e = Env()
    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group,
    )
    print("get_workspace:")
    print(aml_workspace)

    experiment_name = e.experiment_name
    experiment = Experiment(workspace=aml_workspace, name=experiment_name)
    print("create_experiment:")
    print(experiment)

    # Get Azure machine learning cluster
    aml_compute = get_compute(aml_workspace, e.compute_name, e.vm_size)
    if aml_compute is not None:
        print("aml_compute:")
        print(aml_compute)

    # Create a reusable Azure ML environment
    environment = get_environment(
        aml_workspace,
        e.aml_env_name,
        conda_dependencies_file=e.aml_env_train_conda_dep_file,
        create_new=e.rebuild_env,
    )  

    run_config = RunConfiguration()
    run_config.environment = environment

    if e.datastore_name:
        datastore_name = e.datastore_name
    else:
        datastore_name = aml_workspace.get_default_datastore().name
    run_config.environment.environment_variables[
        "DATASTORE_NAME"
    ] = datastore_name  # NOQA: E501

    # model_name_param = PipelineParameter(name="model_name", default_value=e.model_name)  # NOQA: E501


    def_blob_store = Datastore(aml_workspace, e.blobstore_name)

    # # Create a PipelineData to pass data between steps
    # pipeline_data = PipelineData(
    #     "pipeline_data", datastore=def_blob_store
    # )


    calculated_drift_data = PipelineData('calculated_drift_data', datastore=def_blob_store)
    print("PipelineData object created")


    # Get dataset name
    # dataset_name = e.dataset_name

    # data_location = 'aml-training-data'

    # raw_train_data = DataReference(datastore=def_blob_store, 
    #                                   data_reference_name=dataset_name, 
    #                                   path_on_datastore=e.training_data_blobstore_path + '/' + feature_data)


    # def_blob_store.upload(src_dir='./aml_services/' + data_location + '/',
    #                  target_path=e.training_data_blobstore_path,
    #                  overwrite=True)
    baseline_dataset = Dataset.get_by_name(ws, 'train_data_test')
    # target_dataset = Dataset.get_by_name(ws, 'inference-data-distilbert-base-uncased-1-repairclinic-aks')

    calcChiSquareStep = PythonScriptStep(
        name="calculate_chi_square",
        script_name="chi_square.py", 
        arguments=["--input1", baseline_dataset.as_named_input('baseline'),
                #    "--input2", target_dataset.as_named_input('target'),
                   "--output", calculated_drift_data],
        # inputs=[baseline_dataset, target_dataset],
        outputs=[calculated_drift_data],
        compute_target=aml_compute,
        runconfig=run_amlcompute,
        # source_directory=e.sources_directory,
    )
    print("calcChiSquareStep created")

    steps = [calcChiSquareStep]
    
    prediction_monitor_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    prediction_monitor_pipeline._set_experiment_name(e.experiment_name)
    prediction_monitor_pipeline.validate()
    published_pipeline = prediction_monitor_pipeline.publish(
        name=e.pipeline_name,
        description="Model monitor pipeline",
        version=e.build_id,
    )
    print(f"Published pipeline: {published_pipeline.name}")
    print(f"for build {published_pipeline.version}")


if __name__ == "__main__":
    main()

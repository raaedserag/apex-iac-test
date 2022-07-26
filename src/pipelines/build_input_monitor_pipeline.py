import os

from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core import Dataset, Datastore, Experiment, Workspace
from azureml.core.runconfig import RunConfiguration

from aml_services.utils.attach_compute import get_compute
from aml_services.utils.env_variables import Env
from aml_services.utils.manage_environment import get_environment
from utils.schedule import schedule_pipeline


PIPELINE_NAME = EXPERIMENT_NAME = "rprclnc-input-monitor"


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

    # Get Azure machine learning cluster
    aml_compute = get_compute(aml_workspace, e.compute_name, e.vm_size)
    if aml_compute is not None:
        print("aml_compute:")
        print(aml_compute)

    experiment = Experiment(workspace=aml_workspace, name=EXPERIMENT_NAME)
    print("create_experiment:")
    print(experiment)

    # Create a reusable Azure ML environment
    environment = get_environment(
        aml_workspace,
        e.aml_cpu_env_name,
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

    def_blob_store = Datastore(aml_workspace, e.blobstore_name)

    calculated_drift_data = PipelineData('calculated_drift_data', datastore=def_blob_store)
    print("PipelineData object created")

    baseline_dataset = Dataset.get_by_name(aml_workspace, 'train_data_test')
    target_dataset = Dataset.get_by_name(aml_workspace, 'inference-data-distilbert-base-uncased-1-repairclinic-aks')

    calcCosineSimilarityStep = PythonScriptStep(
        name="calculate_cosine_similarity",
        script_name=e.input_monitor_script_path, 
        arguments=["--input1", baseline_dataset.as_named_input('baseline'),
                   "--input2", target_dataset.as_named_input('target'),
                   "--drift_threshold", e.drift_threshold,
                   "--event_endpoint", e.event_endpoint,
                   "--output", calculated_drift_data],
        # inputs=[baseline_dataset, target_dataset],
        outputs=[calculated_drift_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=e.sources_directory,
    )
    print("calcCosineSimilarityStep created")

    steps = [calcCosineSimilarityStep]
    
    monitor_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    monitor_pipeline._set_experiment_name(EXPERIMENT_NAME)
    monitor_pipeline.validate()
    published_pipeline = monitor_pipeline.publish(
        name=PIPELINE_NAME,
        description="Model input monitor pipeline",
        version=e.build_id,
    )
    print(f"Published pipeline: {published_pipeline.name}")
    print(f"for build {published_pipeline.version}")

    # Schedule Pipeline
    schedule_pipeline(aml_workspace, published_pipeline, PIPELINE_NAME, EXPERIMENT_NAME,
                      e.monitor_schedule_frequency, e.monitor_schedule_interval)


if __name__ == "__main__":
    main()

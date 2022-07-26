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
        e.aml_gpu_env_name,
        conda_dependencies_file=e.aml_env_train_conda_dep_file,
        create_new=e.rebuild_env,
        use_gpu=True
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

    model_name_param = PipelineParameter(name="model_name", default_value=e.model_name)  # NOQA: E501


    def_blob_store = Datastore(aml_workspace, e.blobstore_name)

    # Create a PipelineData to pass data between steps
    pipeline_data = PipelineData(
        "pipeline_data", datastore=def_blob_store
    )


    processed_train_data = PipelineData('processed_train_data', datastore=def_blob_store)
    print("PipelineData object created")

    # Get dataset name
    dataset_name = e.dataset_name
    
    raw_train_data = DataReference(datastore=def_blob_store, 
                data_reference_name=dataset_name, 
                path_on_datastore=e.training_data_blobstore_path)

    processTrainDataStep = PythonScriptStep(
        name="process_train_data",
        script_name=e.preprocess_script_path, 
        arguments=["--input", dataset_name,
                   "--output", processed_train_data],
        inputs=[raw_train_data],
        outputs=[processed_train_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=e.sources_directory
    )
    print("preprocessStep created")


    train_eva_step = PythonScriptStep(
        name="train_eva_step",
        script_name=e.train_script_path, 
        arguments=["--input", processed_train_data, "--output", pipeline_data],
        inputs=[processed_train_data],
        outputs=[pipeline_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=e.sources_directory
    )
    print("train_eva_step created")


    evaluate_step = PythonScriptStep(
        name="Evaluate Model ",
        script_name=e.evaluate_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        arguments=[
            "--model_name",
            model_name_param,
            "--allow_run_cancel",
            e.allow_run_cancel,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Evaluate created")

    register_step = PythonScriptStep(
        name="Register Model ",
        script_name=e.register_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        inputs=[pipeline_data],
        arguments=["--step_input", pipeline_data],  # NOQA: E501
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Step Register created")
    # Check run_evaluation flag to include or exclude evaluation step.
    if (e.run_evaluation).lower() == "true":
        print("Include evaluation step before register step.")
        evaluate_step.run_after(train_eva_step)
        register_step.run_after(evaluate_step)
        steps = [train_eva_step, evaluate_step, register_step]
    else:
        print("Exclude evaluation step and directly run register step.")
        register_step.run_after(train_eva_step)
        steps = [train_eva_step, register_step]

    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    train_pipeline._set_experiment_name(e.experiment_name)
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name=e.pipeline_name,
        description="Model training/retraining pipeline",
        version=e.build_id,
    )
    print(f"Published pipeline: {published_pipeline.name}")
    print(f"for build {published_pipeline.version}")


if __name__ == "__main__":
    main()

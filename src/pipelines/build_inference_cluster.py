from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.core import Workspace, Dataset, Datastore
from azureml.core.runconfig import RunConfiguration
from azureml.data.data_reference import DataReference
from pipelines.load_sample_data import create_sample_data_csv
from aml_services.utils.attach_aks import get_aks
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


    # Get Azure machine learning cluster
    aml_aks = get_aks(
        workspace=aml_workspace, 
        compute_name=e.aks_name,
        vm_size=e.vm_size_scoring,
        agent_count=e.aks_agent_count,
        cluster_purpose=e.aks_cluster_purpose
    )
    if aml_aks is not None:
        print("aml_aks:")
        print(aml_aks)

    # Create a reusable Azure ML environment
    environment = get_environment(
        aml_workspace,
        e.aml_env_name_scoring,
        conda_dependencies_file=e.aml_env_score_conda_dep_file,
        create_new=e.rebuild_env,
    )

if __name__ == "__main__":
    main()

import os

from azureml.core import Workspace
from azureml.core import Environment
from azureml.core.model import Model
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AksWebservice

from aml_services.utils.attach_aks import get_aks
from aml_services.utils.env_variables import Env
from aml_services.utils.manage_environment import get_environment


def main():
    e = Env()
    # Get Azure machine learning workspace
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group,
    )

    # Get Azure machine learning cluster
    aml_aks = get_aks(
        workspace=aml_workspace, 
        compute_name=e.aks_name,
        vm_size=e.vm_size_scoring,
        agent_count=e.aks_agent_count,
        cluster_purpose=e.aks_cluster_purpose
    )

    # Create a reusable Azure ML environment
    aml_env = get_environment(
        aml_workspace,
        e.aml_env_name_scoring,
        conda_dependencies_file=e.aml_env_score_conda_dep_file,
        create_new=e.rebuild_env,
        environment_variables=e.ws_env_variables
    )

    entry_script = os.path.join(e.sources_directory, e.score_script)

    # Load the model object
    model = Model(workspace=aml_workspace, name=e.model_name)

    # Define Inference config
    inference_config = InferenceConfig(entry_script=entry_script, environment=aml_env )

    aks_config = AksWebservice.deploy_configuration(autoscale_enabled=True,
                                                    autoscale_min_replicas=1,
                                                    autoscale_max_replicas=2,
                                                    autoscale_refresh_seconds=10,
                                                    autoscale_target_utilization=70,
                                                    auth_enabled=True,
                                                    cpu_cores=1,
                                                    memory_gb=2,
                                                    description='Repair Clinic Scoring web service',
                                                    collect_model_data=True,
                                                    enable_app_insights=True,
                                                    scoring_timeout_ms=60000,
                                                    replica_max_concurrent_requests=2,
                                                    max_request_wait_time=60000
                                                    )

    # Deploy the model
    aks_service = Model.deploy(workspace=aml_workspace,
                            name=e.aks_deployment_name,
                            models=[model],
                            inference_config=inference_config,
                            deployment_config=aks_config,
                            deployment_target=aml_aks,
                            overwrite=True)

    aks_service.wait_for_deployment(show_output=True)
    print(aks_service.state)
      

if __name__ == "__main__":
    main()

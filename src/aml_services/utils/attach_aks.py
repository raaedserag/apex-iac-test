
from azureml.core import Workspace
from azureml.core.compute import AksCompute
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException
from aml_services.utils.env_variables import Env


# Check to see if the cluster already exists

def get_aks(workspace: Workspace, compute_name: str, vm_size: str, agent_count: int, cluster_purpose: str):  # NOQA E501
    try:
        if compute_name in workspace.compute_targets:
            aks_target = workspace.compute_targets[compute_name]
            if aks_target and type(aks_target) is AksCompute:
                print("Found existing compute target " + compute_name + " so using it.") # NOQA
        else:
            e = Env()
            prov_config = AksCompute.provisioning_configuration(
                agent_count=e.aks_agent_count, vm_size=vm_size, cluster_purpose=cluster_purpose

            )
            prov_config.enable_ssl(leaf_domain_label="bapg")

            aks_target = ComputeTarget.create(
                workspace=workspace, name=compute_name, provisioning_configuration=prov_config
            )
            aks_target.wait_for_completion(
                show_output=True
            )
        return aks_target

    except ComputeTargetException as ex:
        print(ex)
        print("An error occurred trying to provision inference cluster.")
        exit(1)
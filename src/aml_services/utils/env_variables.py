"""Env dataclass to load and hold all environment variables
"""
from dataclasses import dataclass
import os
from typing import Optional
import ast
from dotenv import load_dotenv


@dataclass(frozen=True)
class Env:
    """Loads all environment variables into a predefined set of properties
    """

    # to load .env file into environment variables for local execution
    load_dotenv()
    workspace_name: Optional[str] = os.environ.get("WORKSPACE_NAME")
    resource_group: Optional[str] = os.environ.get("RESOURCE_GROUP")
    subscription_id: Optional[str] = os.environ.get("SUBSCRIPTION_ID")
    tenant_id: Optional[str] = os.environ.get("TENANT_ID")
    app_id: Optional[str] = os.environ.get("SP_APP_ID")
    app_secret: Optional[str] = os.environ.get("SP_APP_SECRET")
    vm_size: Optional[str] = os.environ.get("AML_COMPUTE_CLUSTER_CPU_SKU")
    compute_name: Optional[str] = os.environ.get("AML_COMPUTE_CLUSTER_NAME")
    aks_name: Optional[str] = os.environ.get("AKS_COMPUTE_NAME")
    aks_deployment_name: Optional[str] = os.environ.get("AKS_DEPLOYMENT_NAME")
    aks_agent_count: int = int(os.environ.get("AKS_AGENT_COUNT", 2))
    aks_cluster_purpose: Optional[str] = os.environ.get("AKS_CLUSTER_PURPOSE")
    vm_priority: Optional[str] = os.environ.get(
        "AML_CLUSTER_PRIORITY", "lowpriority"
    )  # NOQA: E501
    min_nodes: int = int(os.environ.get("AML_CLUSTER_MIN_NODES", 0))
    max_nodes: int = int(os.environ.get("AML_CLUSTER_MAX_NODES", 2))
    build_id: Optional[str] = os.environ.get("BUILD_BUILDID")
    pipeline_name: Optional[str] = os.environ.get("TRAINING_PIPELINE_NAME")
    monitor_pipeline_name: Optional[str] = os.environ.get("MONITOR_PIPELINE_NAME")
    sources_directory: Optional[str] = os.environ.get(
        "SOURCES_DIR", "aml_services"
    )  # NOQA: E501
    preprocess_script_path: Optional[str] = os.environ.get("PREPROCESS_SCRIPT_PATH",
        "preprocessing/preprocess_repairclinic.py"
    )
    sources_directory_train: Optional[str] = os.environ.get(
        "SOURCES_DIR_TRAIN", "training"
    )  # NOQA: E501
    train_script_path: Optional[str] = os.environ.get("TRAIN_SCRIPT_PATH", 
        "training/training_repairclinic.py"
    )
    evaluate_script_path: Optional[str] = os.environ.get(
        "EVALUATE_SCRIPT_PATH", "evaluate/evaluate_model.py"
    )  # NOQA: E501
    register_script_path: Optional[str] = os.environ.get(
        "REGISTER_SCRIPT_PATH", "register/register_model_repairclinic.py"
    )  # NOQA: E501
    input_monitor_script_path: Optional[str] = os.environ.get(
        "INPUT_MONITOR_SCRIPT_PATH", "monitor/input_monitor.py"
    )
    prediction_monitor_script_path: Optional[str] = os.environ.get(
        "PREDICTION_MONITOR_SCRIPT_PATH", "monitor/performance_monitor.py"
    )
    training_data_blobstore_path = os.environ.get(
        "TRAINING_DATA_BLOBSTORE_PATH", "aml_pipelines_data"                 
    )
    model_name: Optional[str] = os.environ.get("MODEL_NAME")
    experiment_name: Optional[str] = os.environ.get("EXPERIMENT_NAME")
    model_version: Optional[str] = os.environ.get("MODEL_VERSION")
    image_name: Optional[str] = os.environ.get("IMAGE_NAME")
    db_cluster_id: Optional[str] = os.environ.get("DB_CLUSTER_ID")
    score_script: Optional[str] = os.environ.get("SCORE_SCRIPT")
    build_uri: Optional[str] = os.environ.get("BUILD_URI")
    dataset_name: Optional[str] = os.environ.get("DATASET_NAME")
    datastore_name: Optional[str] = os.environ.get("DATASTORE_NAME")
    blobstore_name: Optional[str] = os.environ.get("BLOBSTORE_NAME")
    dataset_version: Optional[str] = os.environ.get("DATASET_VERSION")
    run_evaluation: Optional[str] = os.environ.get("RUN_EVALUATION", "true")
    allow_run_cancel: Optional[str] = os.environ.get(
        "ALLOW_RUN_CANCEL", "true"
    )  # NOQA: E501
    aml_cpu_env_name: Optional[str] = os.environ.get("AML_CPU_ENV_NAME")
    aml_gpu_env_name: Optional[str] = os.environ.get("AML_GPU_ENV_NAME")
    aml_env_train_conda_dep_file: Optional[str] = os.environ.get(
        "AML_ENV_TRAIN_CONDA_DEP_FILE", os.path.abspath(os.path.join(os.path.dirname(__file__),
        '../..', 'environment_setup', 'conda_dependencies_train_gpu.yml'))
    )
    rebuild_env: Optional[bool] = os.environ.get(
        "AML_REBUILD_ENVIRONMENT", False
    )

    ##TODO: Add correct scoring defaults 
    use_gpu_for_scoring: Optional[bool] = os.environ.get(
        "USE_GPU_FOR_SCORING", "false"
    ).lower().strip() == "true"
    aml_env_score_conda_dep_file: Optional[str] = os.environ.get(
        "AML_ENV_SCORE_CONDA_DEP_FILE", os.path.abspath(os.path.join(os.path.dirname(__file__), 
        '../..', 'environment_setup', 'conda_dependencies_scoring.yml'))
    )
    aml_env_scorecopy_conda_dep_file: Optional[str] = os.environ.get(
        "AML_ENV_SCORECOPY_CONDA_DEP_FILE", os.path.abspath(os.path.join(os.path.dirname(__file__),
        '../..', 'environment_setup', 'conda_dependencies_scoring.yml'))
    )
    vm_size_scoring: Optional[str] = os.environ.get(
        "AML_COMPUTE_CLUSTER_CPU_SKU_SCORING"
    )
    compute_name_scoring: Optional[str] = os.environ.get(
        "AML_COMPUTE_CLUSTER_NAME_SCORING"
    )
    vm_priority_scoring: Optional[str] = os.environ.get(
        "AML_CLUSTER_PRIORITY_SCORING", "lowpriority"
    )
    min_nodes_scoring: int = int(
        os.environ.get("AML_CLUSTER_MIN_NODES_SCORING", 0)
    )  # NOQA: E501
    max_nodes_scoring: int = int(
        os.environ.get("AML_CLUSTER_MAX_NODES_SCORING", 4)
    )  # NOQA: E501
    rebuild_env_scoring: Optional[bool] = os.environ.get(
        "AML_REBUILD_ENVIRONMENT_SCORING", "false"
    ).lower().strip() == "true"
    scoring_datastore_storage_name: Optional[str] = os.environ.get(
        "SCORING_DATASTORE_STORAGE_NAME"
    )
    scoring_datastore_access_key: Optional[str] = os.environ.get(
        "SCORING_DATASTORE_ACCESS_KEY"
    )
    scoring_datastore_input_container: Optional[str] = os.environ.get(
        "SCORING_DATASTORE_INPUT_CONTAINER"
    )
    scoring_datastore_input_filename: Optional[str] = os.environ.get(
        "SCORING_DATASTORE_INPUT_FILENAME"
    )
    scoring_datastore_output_container: Optional[str] = os.environ.get(
        "SCORING_DATASTORE_OUTPUT_CONTAINER"
    )
    scoring_datastore_output_filename: Optional[str] = os.environ.get(
        "SCORING_DATASTORE_OUTPUT_FILENAME"
    )
    scoring_dataset_name: Optional[str] = os.environ.get(
        "SCORING_DATASET_NAME"
    )  # NOQA: E501
    scoring_pipeline_name: Optional[str] = os.environ.get(
        "SCORING_PIPELINE_NAME"
    )  # NOQA: E501
    aml_env_name_scoring: Optional[str] = os.environ.get(
        "AML_ENV_NAME_SCORING"
    )  # NOQA: E501
    aml_env_name_score_copy: Optional[str] = os.environ.get(
        "AML_ENV_NAME_SCORE_COPY"
    )  # NOQA: E501
    batchscore_script_path: Optional[str] = os.environ.get(
        "BATCHSCORE_SCRIPT_PATH"
    )  # NOQA: E501
    batchscore_copy_script_path: Optional[str] = os.environ.get(
        "BATCHSCORE_COPY_SCRIPT_PATH"
    )  # NOQA: E501
    ws_env_variables = ast.literal_eval(os.environ.get("SCORE_ENV_VARS"))
    drift_threshold: float = float(os.environ.get("DRIFT_THRESHOLD"))
    event_endpoint: Optional[str] = os.environ.get("EVENT_ENDPOINT")
    train_on_gpu: Optional[bool] =  os.environ.get(
        "TRAIN_ON_GPU", False
    )
    monitor_schedule_frequency: Optional[str] = os.environ.get("MONITOR_SCHEDULE_FREQUENCY")
    monitor_schedule_interval: int = int(os.environ.get("MONITOR_SCHEDULE_INTERVAL"))

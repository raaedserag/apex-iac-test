variable "environment" {}
variable "geo_location" {}
variable "deployment" {}
variable "devops_agent_pool" {}
variable "devops_project_name" {}
variable "pat" {}
variable "key_vault_id" {}
variable "workspace_name" {}
variable "workspace_service_connection" {}
variable "app_resource_group" {}
variable "aml_compute_cluster" {}
variable "storage_account_name" {}
variable "blobstore_name" {
  default = "workspaceblobstore"
}
variable "deploy_to_rc" {
  type = bool
  default = false
}

terraform {
  required_providers {
    azuredevops = {
      source = "microsoft/azuredevops"
      version = ">=0.1.0"
    }
  }
}

locals {
  geo             = "${upper(var.geo_location)}"
  env             = "${upper(var.environment)}"
  geo_lower       = "${lower(var.geo_location)}"
  env_lower       = "${lower(var.environment)}"
  experiment_name = "${var.deployment}-${local.env_lower}-${local.geo_lower}"
}

data "azurerm_subscription" "primary" {
}

data "azurerm_client_config" "current" {
}

data "azuredevops_project" "project" {
  name = var.devops_project_name
}

resource "azuredevops_variable_group" "variablegroup" {
  project_id   = data.azuredevops_project.project.id
  name         = "${var.deployment}-variablegroup"
  description  = "${var.deployment} var grp"
  allow_access = true

  variable {
    name  = "DEPLOYMENT"
    value = var.deployment
  }

  variable {
    name  = "EXPERIMENT_NAME"
    value = local.experiment_name 
  }
  variable {
    name  = "WORKSPACE_NAME"
    value = var.workspace_name
  }

  variable {
    name  = "WORKSPACE_SVC_CONNECTION"
    value = var.workspace_service_connection
  }

  variable {
    name  = "AGENT_POOL"
    value = var.devops_agent_pool
  }

  variable {
    name  = "RESOURCE_GROUP"
    value = var.app_resource_group
  }


  variable {
    name  = "AML_COMPUTE_CLUSTER_NAME"
    value = var.aml_compute_cluster
  }

  variable {
    name  = "DATASTORE_NAME"
    value = var.storage_account_name
  }

  variable {
    name  = "BLOBSTORE_NAME"
    value = var.blobstore_name 
  }

} 

#TODO: add any other needed vars for devops 
#    app_id: Optional[str] = os.environ.get("SP_APP_ID")
#    app_secret: Optional[str] = os.environ.get("SP_APP_SECRET")
#    vm_size: Optional[str] = os.environ.get("AML_COMPUTE_CLUSTER_CPU_SKU")

#output "repo_url" {
#  value = azuredevops_git_repository.repo.remote_url
#}

#output "agent_pool" {
#  value = azuredevops_agent_pool.pool.name
#}

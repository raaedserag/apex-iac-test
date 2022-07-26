terraform {
  required_providers {
    azuredevops = {
      source  = "microsoft/azuredevops"
      version = "=0.2.2"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=3.15.1"
    }
  }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
  skip_provider_registration = true
}
provider "azuredevops" {
  personal_access_token = var.ado_pat
  org_service_url       = var.ado_org
}

data "azurerm_resource_group" "main_resources_group" {
  name = var.resources_group
}

locals {
  geo_location    = data.azurerm_resource_group.main_resources_group.location
  resourcesPrefix = var.namespace
}

############################## Devops Module ##############################
module "devops" {
  source                       = "./modules/devops"
  resourcesPrefix              = local.resourcesPrefix
  resources_group              = data.azurerm_resource_group.main_resources_group.name
  ado_project_name             = var.ado_project
  github_personal_access_token = var.github_pat
  github_repository           = var.github_repository
  github_branch                = var.github_branch
  pipeline_definition_path     = var.pipeline_definition_path
}
############################## Devops Module ##############################

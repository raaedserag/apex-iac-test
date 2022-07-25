terraform {
  required_providers {
    azuredevops = {
      source = "microsoft/azuredevops"
      version = ">=0.1.0"
    }
  }
}

provider "azurerm" {
  features {
      key_vault {
      purge_soft_delete_on_destroy = true
    }
  }
#  client_id = var.azure_client_id
#  client_secret = var.azure_client_secret
  skip_provider_registration = true
}

provider "azuredevops" {
  personal_access_token = var.pat
  org_service_url       = "https://dev.azure.com/apexdatahub"
}
locals {
  environment_list = toset([
    "dev"
    ])
}

# data "http" "myip" {
#   url = "http://ipv4.icanhazip.com"
# }

# locals {
#   my_ip_address = chomp(data.http.myip.body)
# }

#resource "azurerm_resource_group" "burke_repair_clinic" {
#  for_each = local.environment_list
#  name     = "${var.deployment}-${each.key}-mlops"
#  location = var.geo_location
#}

data azurerm_resource_group "burke_repair_clinic" {
  name = var.resource_group
}

module "key_vault" {
  for_each           = local.environment_list
  app_resource_group = data.azurerm_resource_group.burke_repair_clinic.name
  caller_oid         = var.caller_oid
  deployment         = var.deployment
  environment        = each.key
  geo_location       = "${var.geo_location}"
  source             = "./modules/kvault"
}

module "storage" {
  for_each                    = local.environment_list
  app_resource_group          = data.azurerm_resource_group.burke_repair_clinic.name
  app_resource_group_location = data.azurerm_resource_group.burke_repair_clinic.location
  deployment                  = var.deployment
  environment                 = each.key
  geo_location                = var.geo_location
  key_vault_id                = module.key_vault["${each.key}"].key_vault_id
  source                      = "./modules/storage"
}

module "azure_ml_ws" {
  for_each                    = local.environment_list
  app_resource_group          = data.azurerm_resource_group.burke_repair_clinic.name
  app_resource_group_location = data.azurerm_resource_group.burke_repair_clinic.location
  environment                 = each.key
  deployment                  = var.deployment
  geo_location                = var.geo_location
  key_vault_id                = module.key_vault["${each.key}"].key_vault_id
  source                      = "./modules/azml"
  storage_account             = module.storage["${each.key}"].storage_account_id
}

module "devops" {
  for_each                     = local.environment_list
  app_resource_group           = data.azurerm_resource_group.burke_repair_clinic.name
  aml_compute_cluster          = module.azure_ml_ws["${each.key}"].aml_compute_cluster
  environment                  = each.key
  deployment                   = var.deployment
  devops_agent_pool            = var.devops_agent_pool
  devops_project_name          = var.devops_project_name
  geo_location                 = var.geo_location
  pat                          = var.pat
  key_vault_id                 = module.key_vault["${each.key}"].key_vault_id
  storage_account_name         = module.storage["${each.key}"].storage_account_name
  workspace_name               = module.azure_ml_ws["${each.key}"].workspace_name
  workspace_service_connection = var.workspace_service_connection
  source                       = "./modules/devops"
}
variable "environment" {}
variable "geo_location" {}
variable "deployment" {}

variable "app_resource_group" {}
variable "app_resource_group_location" {}
variable "key_vault_id" {}

locals {
  geo       = "${upper(var.geo_location)}"
  env       = "${upper(var.environment)}"
  geo_lower = "${lower(var.geo_location)}"
  env_lower = "${lower(var.environment)}"
}

locals {
  app_resource_storage_name = "${var.deployment}adls01"
}

data "azurerm_client_config" "current" {}

resource "azurerm_storage_account" "app" {
  name                     = local.app_resource_storage_name
  resource_group_name      = var.app_resource_group
  location                 = var.app_resource_group_location
  account_kind             = "StorageV2"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = "${local.env}"
  }
}

output "storage_account_id" {
  value = azurerm_storage_account.app.id
}

output "storage_account_name" {
  value = local.app_resource_storage_name
}

output "storage_account_conn_str" {
  value = azurerm_storage_account.app.primary_connection_string
}
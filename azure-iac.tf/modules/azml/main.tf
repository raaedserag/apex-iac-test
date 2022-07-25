variable "environment" {}
variable "geo_location" {}
variable "deployment" {}

variable "key_vault_id" {}
variable "app_resource_group" {}
variable "storage_account" {}
variable "app_resource_group_location" {}

locals {
  geo       = "${upper(var.geo_location)}"
  env       = "${upper(var.environment)}"
  geo_lower = "${lower(var.geo_location)}"
  env_lower = "${lower(var.environment)}"
}

data "azurerm_client_config" "current" {}

resource "azurerm_application_insights" "web" {
  name                = "${var.deployment}-appinsights"
  location            = var.app_resource_group_location
  resource_group_name = var.app_resource_group
  application_type    = "web"
}

resource "azurerm_machine_learning_workspace" "this" {
  name                    = "${var.deployment}-mlws"
  location                = var.app_resource_group_location
  application_insights_id = azurerm_application_insights.web.id
  resource_group_name     = var.app_resource_group
  key_vault_id            = var.key_vault_id
  storage_account_id      = var.storage_account
  identity {
    type = "SystemAssigned"
  }
  lifecycle {
    ignore_changes = [
      tags,
      application_insights_id,
      container_registry_id,
      high_business_impact
    ]
  }
}

resource "azurerm_container_registry" "aml" {
  name                     = "${var.deployment}conreg"
  resource_group_name      = var.app_resource_group
  location                 = var.app_resource_group_location
  sku                      = "Standard"
  admin_enabled            = true
}

resource "azurerm_machine_learning_compute_cluster" "this" {
  name                          = "${var.deployment}-cl"
  location                      = var.app_resource_group_location
  vm_priority                   = "Dedicated"
  vm_size                       = "STANDARD_NC6"
  machine_learning_workspace_id = azurerm_machine_learning_workspace.this.id

  scale_settings {
    min_node_count                       = 0
    max_node_count                       = 2
    scale_down_nodes_after_idle_duration = "PT30S" # 30 seconds
  }

  identity {
    type = "SystemAssigned"
  }
}

output "workspace_id" {
  value = azurerm_machine_learning_workspace.this.id
}

output "workspace_name" {
  value = "${var.deployment}-mlws"
}

output "aml_compute_cluster" {
  value = "${var.deployment}-cl"
}
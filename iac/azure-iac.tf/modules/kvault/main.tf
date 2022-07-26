variable "environment" {}
variable "geo_location" {}
variable "deployment" {}
variable "caller_oid" {}
variable "app_resource_group" {}

locals {
  geo = "${upper(var.geo_location)}"
  env = "${upper(var.environment)}"
  geo_lower = "${lower(var.geo_location)}"
  env_lower = "${lower(var.environment)}"
}

locals {
  key_vault_name = "${var.deployment}-${local.env_lower}-kv"
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault" "app" {
  # Should be unique name
  name                        = "${local.key_vault_name}-mlops"
  location                    = local.geo_lower
  resource_group_name         = var.app_resource_group
  enabled_for_disk_encryption = true
  enabled_for_deployment      = true
  tenant_id                   = data.azurerm_client_config.current.tenant_id
  purge_protection_enabled    = false
  enable_rbac_authorization   = true

  sku_name = "standard"
}


output "key_vault_id" {
  value = azurerm_key_vault.app.id
}

output "client_config_object_id" {
  value = data.azurerm_client_config.current.object_id
}

output "client_config_client_id" {
  value = data.azurerm_client_config.current.client_id
}
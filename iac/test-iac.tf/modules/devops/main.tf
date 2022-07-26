
terraform {
  required_providers {
    azuredevops = {
      source  = "microsoft/azuredevops"
      version = "=0.2.2"
    }
  }
}

data "azuredevops_project" "apexml_project" {
  name = var.ado_project_name
}

locals {
  resourcesPrefix = var.resourcesPrefix
}

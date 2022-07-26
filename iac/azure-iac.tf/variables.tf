variable "environment" {
  description = "Please choose an environment: (dev | stg | prod)"
}
variable "resource_group" {
  description = "resource group for deployment"
}

variable "deployment" {
  description = "deployment name identifier"
}

variable "environment_list" {
  description = "Environment ID"
  type        = list(any)
}

variable "geo_location" {
  description = "Please choose a geo location"
}

variable "workspace_service_connection" {
  description = "devops workspace service connection"
}

variable "devops_agent_pool" {
  description = "Agent Pool Name"
}

variable "devops_project_name" {
  description = "devops project name"
}

variable "caller_oid" {
  description = "deployer AD object ID"
}


variable "pat" {
  type = string
}

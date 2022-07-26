variable "namespace" {
  type        = string
  description = "Please enter the resources namespace."
}

variable "resources_group" {
  type        = string
  description = "Please enter the name of the existing resource group."
}

variable "ado_pat" {
  type        = string
  description = "Please enter the Azure DevOps PAT."
  sensitive   = true
}
variable "ado_org" {
  type        = string
  description = "Please enter the existing Azure DevOps organization."
}
variable "ado_project" {
  type        = string
  description = "Please enter the existing Azure DevOps project."
}

variable "github_pat" {
  type        = string
  description = "Please enter the GitHub repository PAT."
  sensitive   = true
}

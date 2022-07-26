variable "resourcesPrefix" {
  type        = string
  description = "Namespace for the resources"
}
variable "resources_group" {
  type        = string
  description = "Variables_Group: RESOURCE_GROUP"
}

variable "ado_project_name" {
  type        = string
  description = "Existing Azure DevOps Project Name"
}

variable "github_personal_access_token" {
  type        = string
  description = "Github Personal Access Token"
}
variable "github_repository" {
  type        = string
  description = "Github Repository"
}
variable "github_branch" {
  type        = string
  description = "Github Branch"
}
variable "pipeline_definition_path" {
  type        = string
  description = "Please enter the Azure Pipeline definition path."
}
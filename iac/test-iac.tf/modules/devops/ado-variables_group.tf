
resource "azuredevops_variable_group" "variablegroup" {
  project_id   = data.azuredevops_project.main_project.id
  name         = "${local.resourcesPrefix}-environment"
  description  = "variables group to be used for the environment"
  allow_access = true

  variable {
    name  = "RESOURCE_GROUP"
    value = var.resources_group
  }
  variable {
    name  = "TEST"
    value = "SERAG"
  }

}

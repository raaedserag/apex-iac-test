
resource "azuredevops_variable_group" "infrastructure_vg" {
  project_id   = data.azuredevops_project.apexml_project.id
  name         = "${local.resourcesPrefix}-infrastructure-parameters"
  description  = "variables group to be used for the environment"
  allow_access = true

  variable {
    name  = "RESOURCE_GROUP"
    value = var.resources_group
  }
  variable {
    name  = "TEST_VARIABLE"
    value = "SERAG"
  }

}

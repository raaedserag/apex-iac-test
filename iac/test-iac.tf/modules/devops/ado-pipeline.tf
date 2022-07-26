resource "azuredevops_serviceendpoint_github" "example" {
  project_id            = data.azuredevops_project.main_project.id
  service_endpoint_name = "${local.resourcesPrefix}-github-serviceendpoint"

  auth_personal {
    personal_access_token = var.github_personal_access_token
  }
}

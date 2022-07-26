resource "azuredevops_serviceendpoint_github" "apex_repository" {
  project_id            = data.azuredevops_project.apexml_project.id
  service_endpoint_name = "${local.resourcesPrefix}-github-serviceendpoint"

  auth_personal {
    personal_access_token = var.github_personal_access_token
  }
}

resource "azuredevops_build_definition" "example" {
  project_id = data.azuredevops_project.apexml_project.id
  name       = "${local.resourcesPrefix}-build"
#   path       = "devops"
  repository {
    service_connection_id = azuredevops_serviceendpoint_github.apex_repository.id
    repo_type             = "GitHub"
    repo_id               = "${var.github_repository}"
    branch_name           = "${var.github_branch}"
    yml_path              = "devops/azure-pipelines.yml"
  }

}

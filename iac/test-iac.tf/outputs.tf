# output "module_devops" {
#   value = module.devops
# }

# output "module_azml" {
#   value = module.azure_ml_ws
# }

# output "module_keyvault" {
#   value = module.key_vault
# }

output "pipeline_infrastructur_vg" {
  value       = module.devops.pipeline_infrastructur_vg_name
  description = "Pipeline Infrastructure Variables Group Name"
}
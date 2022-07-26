## Repair Prediction IAC


How to create service principal?
https://docs.microsoft.com/en-us/cli/azure/create-an-azure-service-principal-azure-cli#4-sign-in-using-a-service-principal

```sh
    az login
    az ad sp create-for-rbac --display-name apex-iac-sp --role owner --scopes /subscriptions/697f84d3-5f2d-4681-a5b4-f0e8ee6920b8
    az ad sp list --display-name apex-iac-sp
```


## Prerequisites
- Azure login (human or service provider)
- valid .env file contains at least: (ARM_SUBSCRIPTION_ID, ARM_TENANT_ID, ADO_PAT, & GITHUB_PAT)
## Prerequisite resources
You must have the following resources and provide them in default terraform variables & runway variables
- Backend resources group
- Backend storage account
- Backend storage container
- Main resources group (can be the same as Backend resources group)
- Azure Devops Organization
- Azure Devops Project
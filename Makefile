#!make
include .env
export $(shell sed 's/=.*//' .env)

# Take First argument only
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)
Environment := $(wordlist 1,1,${RUN_ARGS})

# Set default environment as "arm"
ifeq ($(Environment),)
Environment := "arm"
endif

initialize:
	cd iac; pipenv install iac
plan:
	cd iac; DEPLOY_ENVIRONMENT=${Environment} pipenv run runway plan --ci

deploy:
	cd iac; DEPLOY_ENVIRONMENT=${Environment} pipenv run runway deploy --ci

destroy:
	cd iac; DEPLOY_ENVIRONMENT=${Environment} pipenv run runway destroy --ci

# Take First argument only
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)
Environment := $(wordlist 1,1,${RUN_ARGS})

# Set default environment as "arm"
ifeq ($(Environment),)
Environment := "arm"
endif

initialize:
	pipenv install
plan:
	source env.bashrc
	DEPLOY_ENVIRONMENT=${Environment} pipenv run runway plan --ci

deploy:
	source env.bashrc
	DEPLOY_ENVIRONMENT=${Environment} pipenv run runway deploy --ci

destroy:
	source env.bashrc
	DEPLOY_ENVIRONMENT=${Environment} pipenv run runway destroy --ci

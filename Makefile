SHELL := /bin/bash
STACK_NAME := media-service
REGION := us-east-1
PROFILE := default

.PHONY: help build deploy-local logs delete-local clean

help:
	@echo "Available targets:"
	@echo "  make build          - Build the SAM project"
	@echo "  make deploy-local   - Deploy to LocalStack"
	@echo "  make logs           - Tail logs for a function"
	@echo "  make delete-local   - Delete the stack from LocalStack"
	@echo "  make clean          - Clean up .aws-sam build artifacts"

# Build your Lambda functions
build:
	sam build

# Deploy into LocalStack
deploy-local: build
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=$(REGION) \
	samlocal deploy \
		--stack-name $(STACK_NAME) \
		--resolve-s3 \
		--region $(REGION) \
		--capabilities CAPABILITY_IAM \
		--no-confirm-changeset \
		--no-fail-on-empty-changeset

# Tail logs for a function (e.g. make logs FUNC=UploadFunction)
logs:
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=$(REGION) \
	samlocal logs \
		--stack-name $(STACK_NAME) \
		--name $(FUNC) \
		--region $(REGION)

# Delete the stack in LocalStack
delete-local:
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=$(REGION) \
	samlocal delete \
		--stack-name $(STACK_NAME) \
		--region $(REGION) \
		--no-prompts

# Remove build artifacts
clean:
	rm -rf .aws-sam

# start api gateway
start-api:
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test AWS_DEFAULT_REGION=$(REGION) \
	samlocal local start-api --docker-network media-service_localstack-net

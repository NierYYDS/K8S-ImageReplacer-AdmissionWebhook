WEBHOOK_SERVICE?=image-replacer-service
NAMESPACE?=default
CONTAINER_REPO?=docker.io/nieryyds/image-replacer-webhook
CONTAINER_VERSION?=0.1.2
CONTAINER_IMAGE=$(CONTAINER_REPO):$(CONTAINER_VERSION)

.PHONY: docker-build
docker-build:
	docker build -t $(CONTAINER_IMAGE) .

.PHONY: docker-push
docker-push:
	docker push $(CONTAINER_IMAGE) 

.PHONY: k8s-deploy
k8s-deploy: k8s-deploy-other k8s-deploy-csr k8s-deploy-deployment

.PHONY: k8s-deploy-other
k8s-deploy-other:
	kubectl apply -k deploy/other
	kubectl apply -k deploy/csr
	@echo Waiting for cert creation ...
	@sleep 15
	kubectl certificate approve $(WEBHOOK_SERVICE).$(NAMESPACE)

.PHONY: k8s-deploy-csr
k8s-deploy-csr:
	kustomize build deploy/csr | kubectl apply -f -
	@echo Waiting for cert creation ...
	@sleep 15
	kubectl certificate approve $(WEBHOOK_SERVICE).$(NAMESPACE)

.PHONY: k8s-deploy-deployment
k8s-deploy-deployment:
	(cd deploy/deployment && \
	kustomize edit set image CONTAINER_IMAGE=$(CONTAINER_IMAGE))
	kustomize build deploy/deployment | kubectl apply -f -

.PHONY: k8s-delete-all
k8s-delete-all:
	kustomize build deploy/other | kubectl delete --ignore-not-found=true -f  - 
	kustomize build deploy/csr | kubectl delete --ignore-not-found=true -f  - 
	kustomize build deploy/deployment | kubectl delete --ignore-not-found=true -f  - 
	kubectl delete --ignore-not-found=true csr $(WEBHOOK_SERVICE).$(NAMESPACE)
	kubectl delete --ignore-not-found=true secret hello-tls-secret

.PHONY: test
test:
	pytest
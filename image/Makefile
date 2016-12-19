.PHONY:	build push

REGISTRY=freehandocker
IMAGE=debug
TAG=v1

build:
	docker build -t $(REGISTRY)/$(IMAGE):$(TAG) ./

push: build
	docker push $(REGISTRY)/$(IMAGE):$(TAG)
	docker tag $(REGISTRY)/$(IMAGE):$(TAG) $(REGISTRY)/$(IMAGE):latest
	docker push $(REGISTRY)/$(IMAGE):latest
	docker rmi $(REGISTRY)/$(IMAGE):latest

all: push

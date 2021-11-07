COMPANY    = ogarantia/
PROJECT    = ausdeep/engine
NAME       = $(COMPANY)$(PROJECT)
COMMIT     = $(shell git log -1 --pretty=%h)
VERSION    = 0.1.0
TF         = tf2.4.1
DEVICE     = gpu
TAG        = $(VERSION)-$(TF)-$(DEVICE)
IMG_DEV    = ghcr.io/$(NAME):py-$(TAG)
IMG_CYTHON = ghcr.io/$(NAME):cython-$(TAG)
VOLUME     = /opt/ausdeep-engine


# Build development container.
.PHONY: build
build:
	docker build -t $(IMG_DEV) -f dockerfile .

# Build cython container.
.PHONY: build_cython
build_cython:
	docker build -t $(IMG_CYTHON) -f dockerfile.cython .

# Run container (cython).
.PHONY: run
run:
	@docker run -it --rm --gpus all \
		-v ${PWD}:$(VOLUME) \
		$(IMG_CYTHON) \
		bash

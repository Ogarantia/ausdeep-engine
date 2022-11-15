COMPANY    = ogarantia/
PROJECT    = ausdeep/engine
NAME       = $(COMPANY)$(PROJECT)
COMMIT     = $(shell git log -1 --pretty=%h)
VERSION    = 0.1.0
TF         = tf2.8.3
DEVICE     = cpu
ARCH       = `arch`
PLATFORM   = linux/$(ARCH)
TAG        = $(VERSION)-$(TF)-$(DEVICE)-$(ARCH)
IMG_DEV    = ghcr.io/$(NAME):py-$(TAG)
IMG_CYTHON = ghcr.io/$(NAME):cython-$(TAG)
VOLUME     = /opt/ausdeep-engine


.PHONY: arch
arch:
	@echo $(ARCH)
	@echo $(PLATFORM)
	@echo $(TAG)
	@echo $(IMG_DEV)

# Build development container.
.PHONY: build
build:
    # Symbolic link to dockerfiles
	rm dockerfile

	ln -s dockerfiles/dockerfile.$(TF).$(DEVICE) dockerfile

	DOCKER_BUILDKIT=0 docker buildx build --no-cache --platform $(PLATFORM) -t $(IMG_DEV) -f dockerfile .

# Build cython container.
.PHONY: build_cython
build_cython:
    # Symbolic link to dockerfiles
	rm dockerfile.cython

	ln -s dockerfiles/dockerfile.$(TF).$(DEVICE).cython dockerfile.cython

	DOCKER_BUILDKIT=0 docker buildx build --no-cache --platform $(PLATFORM) -t $(IMG_CYTHON) -f dockerfile.cython .

# Run container (python).
.PHONY: run
run:
ifeq ($(DEVICE),gpu)
	@docker run -it --rm --gpus all \
		-v ${PWD}:$(VOLUME) \
		$(IMG_DEV) \
		bash
else
	@docker run -it --rm \
		-v ${PWD}:$(VOLUME) \
		$(IMG_DEV) \
		bash
endif

# Run container (cython).
.PHONY: run_cython
run_cython:
ifeq ($(DEVICE),gpu)
	@docker run -it --rm --gpus all \
		-v ${PWD}:$(VOLUME) \
		$(IMG_CYTHON) \
		bash
else
	@docker run -it --rm \
		-v ${PWD}:$(VOLUME) \
		$(IMG_CYTHON) \
		bash
endif

# Build development container
.PHONY: push
push:
	@docker push $(IMG_DEV)
	@docker push $(IMG_CYTHON)



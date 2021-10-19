build:
	docker build -t ogarantia/ausdeep/engine:py-0.1.0-tf2.3.0-gpu .

run:
	@docker run -it --rm --gpus all --privileged \
		-v $$(pwd):/opt \
		ogarantia/ausdeep/engine-py-0.1.0-tf2.3.0-gpu \
		bash

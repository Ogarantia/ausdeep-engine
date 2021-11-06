build:
	docker build -t ogarantia/ausdeep/engine:py-0.1.0-tf2.4.1-gpu .

run:
	@docker run -it --rm --gpus all \
		-v ${PWD}:/opt/ausdeep-engine \
		ogarantia/ausdeep/engine:py-0.1.0-tf2.4.1-gpu \
		bash

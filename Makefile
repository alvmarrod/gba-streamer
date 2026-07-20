IMAGE_NAME=gba-streamer
IMAGE_VERSION?=$(shell grep ^version pyproject.toml | cut -d'"' -f2)
CONTAINER_NAME=gba-streamer
NETWORK_NAME=proxy-network

build:
	docker build -t ${IMAGE_NAME}:${IMAGE_VERSION} .

run:
	docker run \
		--restart unless-stopped \
		--name ${CONTAINER_NAME} \
		--network ${NETWORK_NAME} \
		-d \
		--env-file .env \
		-v `pwd`/saves:/app/saves \
		-v `pwd`/roms:/app/roms:ro \
		-v `pwd`/config:/app/config:ro \
		-p 8080:8080 \
		${IMAGE_NAME}:${IMAGE_VERSION}

stop:
	-docker stop ${CONTAINER_NAME}
	-docker rm ${CONTAINER_NAME}

logs:
	docker logs -f ${CONTAINER_NAME}

deploy: build stop run

test:
	uv run pytest tests/ -v

bench:
	uv run pytest tests/performance/ --benchmark-only -q

run:
	flask --app api_endpoint_models/app run --debug --host=0.0.0.0

docker_compose_down:
	docker-compose down
	Remove-Item -Recurse -Force infra/postgresql/data
up_docker_compose:
	docker-compose -f ./infra/postgresql/compose.yaml up -d
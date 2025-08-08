# Variáveis
COMPOSE_FILE=docker-compose.yml
FASTAPI_SERVICE=fastapi

.PHONY: up down restart shell logs build test clean test-cov

# Sobe todos os serviços em background
up:
	docker compose -f $(COMPOSE_FILE) up -d

# Desliga todos os serviços
down:
	docker compose -f $(COMPOSE_FILE) down

# Reconstrói a imagem do fastapi e sobe os serviços
build:
	docker compose -f $(COMPOSE_FILE) build $(FASTAPI_SERVICE)

# Reinicia o serviço fastapi
restart:
	docker compose -f $(COMPOSE_FILE) restart $(FASTAPI_SERVICE)

# Abre shell interativo no container fastapi
shell:
	docker exec -it $(FASTAPI_SERVICE) bash

# Visualiza logs do fastapi em tempo real
logs:
	docker logs -f $(FASTAPI_SERVICE)

# Roda os testes dentro do container fastapi
test:
	docker exec -it $(FASTAPI_SERVICE) bash -c "pytest tests -v"

# Remove containers, redes, volumes e imagens não usados (limpeza)
clean:
	docker system prune -f

test-cov:
	docker exec -it $(FASTAPI_SERVICE) bash -c "pytest --cov=app --cov-report=term-missing"
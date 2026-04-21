NETWORK = rag-agent-network
LANGFUSE = rag-agent-langfuse
API = rag-agent-api

.PHONY: help

help:
	@echo "Targets disponíveis:"
	@echo "  make build     - Constrói e sobe todos os serviços"
	@echo "  make up        - Sobe todos os serviços"
	@echo "  make down      - Derruba todos os serviços"
	@echo "  make reset     - down + remove todos os volumes"
	@echo "Obs. 1: Os comandos consideram que o langfuse utilizado é local."

# Se a rede não existir, a criamos
network:
	docker network inspect $(NETWORK) >/dev/null 2>&1 || \
	docker network create $(NETWORK)

build: network
	docker-compose -p $(LANGFUSE) -f langfuse/docker-compose.yml up -d --build
	docker-compose -p $(API) -f docker-compose.yml up -d --build

up: network
	docker-compose -p $(LANGFUSE) -f langfuse/docker-compose.yml up -d
	docker-compose -p $(API) -f docker-compose.yml up -d

down:
	docker-compose -p $(LANGFUSE) -f langfuse/docker-compose.yml down
	docker-compose -p $(API) -f docker-compose.yml down

reset:
	docker-compose -f langfuse/docker-compose.yml down -v
	docker-compose -f docker-compose.yml down -v

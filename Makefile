build:
	docker-compose -p "rag-agent-api" -f docker-compose.yml up --build

up:
	docker-compose -p "rag-agent-api" -f docker-compose.yml up
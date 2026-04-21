## Configuração do Langfuse

Os comandos `make` assumem que existe uma pasta `langfuse/` com o `docker-compose.yml` do Langfuse. Como ela não é versionada neste repositório, é necessário configurá-la manualmente antes do primeiro uso.

1. Clone o repositório do Langfuse dentro deste projeto:
    ```shell
    git clone https://github.com/langfuse/langfuse.git
    ```

2. Adicione o bloco de rede ao final de `langfuse/docker-compose.yml`:
    ```yml
    networks:
      default:
        name: rag-agent-network
        external: true
    ```

3. Em http://localhost:3000 (interface web do Langfuse):
    1. Crie um acesso
    2. Adicione uma organização e um projeto
    3. Crie as chaves de conexão em `Settings -> API Keys`

4. Crie o arquivo `api/.env` a partir do `api/.env.example` e preencha as variáveis:
    ```shell
    LANGFUSE_SECRET_KEY=sk-lf-...
    LANGFUSE_PUBLIC_KEY=pk-lf-...
    LANGFUSE_BASE_URL=http://langfuse-web:3000
    ```
    > Use `http://langfuse-web:3000` e não `localhost` — os serviços se comunicam pela rede Docker interna.

## Comandos

| Comando | Descrição |
|---|---|
| `make build` | Constrói as imagens e sobe todos os serviços |
| `make up` | Sobe todos os serviços sem rebuildar |
| `make down` | Derruba todos os serviços |
| `make reset` | Derruba todos os serviços e remove os volumes |

Para adicionar pacotes Python:
```shell
uv add --project api <package>
```

## Observações

- O modelo de embedding utilizado é leve e roda eficientemente em CPU. A versão do Torch no projeto é a versão CPU (sem CUDA), mantendo a imagem Docker enxuta.
- O chunking aplicado a PDFs é feito separando páginas.

## TODO
- Adicionar autenticação/credenciais na API
- Adicionar memória de curto e longo prazo aos agentes

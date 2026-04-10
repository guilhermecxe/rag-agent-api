## Comandos

- Para construir e subir o serviço:
    ```shell
    make build
    ```

- Para subir o serviço:
    ```shell
    make build
    ```

- Para adicionar pacotes:
    ```bash
    uv add --project api <package>
    ```

## Observações

- Como o modelo de embedding utilizado no projeto é leve e pode ser executado de forma eficiente na CPU, a versão do Torch utilizada é a versão CPU, sem a dependência de CUDA. Isso garante uma imagem Docker ajustada aos requisitos do projeto, sem incluir componentes desnecessários para a execução do modelo de embedding.

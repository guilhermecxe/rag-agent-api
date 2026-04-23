from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os


_bearer = HTTPBearer(auto_error=False)

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> None:
    """Verifica a chave de API enviada no cabeçalho Authorization.

    Em ambiente de desenvolvimento (``ENVIRONMENT=dev``) a verificação é ignorada.
    Caso contrário, o token Bearer deve corresponder à variável de ambiente ``API_KEY``.

    Args:
        credentials (HTTPAuthorizationCredentials | None): Credenciais extraídas do
            cabeçalho ``Authorization: Bearer <token>``.

    Raises:
        HTTPException: 401 Unauthorized quando as credenciais estão ausentes ou inválidas.
    """
    if os.environ.get("ENVIRONMENT", "prod") == "dev":
        return

    if credentials is None or credentials.credentials != os.environ.get("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

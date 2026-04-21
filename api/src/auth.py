from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os


_bearer = HTTPBearer(auto_error=False)

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> None:
    if os.environ.get("ENVIRONMENT", "prod") == "dev":
        return

    if credentials is None or credentials.credentials != os.environ.get("API_KEY"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

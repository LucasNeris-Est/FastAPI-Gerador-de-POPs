from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua_chave_secreta_padrao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class JWTBearer(HTTPBearer):
    def _init_(self, auto_error: bool = True):
        super(JWTBearer, self)._init_(auto_error=auto_error)

    async def _call_(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self)._call_(
            request
        )

        if not credentials:
            raise HTTPException(
                status_code=403, detail="Credenciais de autenticação não fornecidas"
            )

        if credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=403, detail="Esquema de autenticação inválido"
            )

        if not self.verify_jwt(credentials.credentials):
            raise HTTPException(status_code=403, detail="Token inválido ou expirado")

        return credentials.credentials

    def verify_jwt(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

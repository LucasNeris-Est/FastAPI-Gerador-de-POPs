import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional


class DownloadManager:
    def __init__(self):
        self._download_tokens: Dict[str, Dict] = {}

    def create_download_token(self, filename: str, user_id: str) -> str:
        """Cria um token único para download."""
        token = secrets.token_urlsafe(32)
        expiry = datetime.utcnow() + timedelta(minutes=5)  # Token válido por 5 minutos

        self._download_tokens[token] = {
            "filename": filename,
            "user_id": user_id,
            "expiry": expiry,
        }

        return token

    def validate_token(self, token: str) -> Optional[str]:
        """Valida o token e retorna o nome do arquivo se válido."""
        if token not in self._download_tokens:
            return None

        token_data = self._download_tokens[token]

        if datetime.utcnow() > token_data["expiry"]:
            del self._download_tokens[token]
            return None

        # Token válido - remover após uso
        filename = token_data["filename"]
        del self._download_tokens[token]
        return filename

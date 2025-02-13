import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json
from typing import Any, Dict


class APILogger:
    def __init__(self):
        # Criar diretório de logs se não existir
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)

        # Configurar logger principal
        self.logger = logging.getLogger("api_logger")
        self.logger.setLevel(logging.INFO)

        # Configurar formato do log
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Handler para arquivo com rotação
        file_handler = RotatingFileHandler(
            os.path.join(self.logs_dir, "api.log"),
            maxBytes=10485760,  # 10MB
            backupCount=5,
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Configurar logger de segurança separado
        self.security_logger = logging.getLogger("security_logger")
        self.security_logger.setLevel(logging.INFO)

        security_handler = RotatingFileHandler(
            os.path.join(self.logs_dir, "security.log"),
            maxBytes=10485760,
            backupCount=5,
        )
        security_handler.setFormatter(formatter)
        self.security_logger.addHandler(security_handler)

    def log_request(
        self, request: Any, response: Any = None, error: Exception = None
    ) -> None:
        """Registra detalhes da requisição e resposta"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": getattr(request, "method", "N/A"),
            "url": str(getattr(request, "url", "N/A")),
            "client_ip": getattr(request, "client.host", "N/A"),
            "status_code": getattr(response, "status_code", 500 if error else "N/A"),
        }

        if error:
            log_data["error"] = str(error)
            self.logger.error(f"Request failed: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Request processed: {json.dumps(log_data)}")

    def log_security_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Registra eventos de segurança"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            **details,
        }
        self.security_logger.warning(f"Security event: {json.dumps(log_data)}")

    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Registra erros do sistema"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
        }
        self.logger.error(f"System error: {json.dumps(log_data)}")


# Instância global do logger
api_logger = APILogger()

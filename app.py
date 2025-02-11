from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from guardrails import Guard
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from Validador_tex import ValidTex  # Certifique-se de importar o validador criado
from utils import (
    extract_tex_content,
    compile_latex,
    extract_text_from_pdf,
    chat_with_persona,
)
from auth import JWTBearer, create_access_token, SECRET_KEY, ALGORITHM
from fastapi.security import HTTPBasicCredentials
from typing import Dict
from download_manager import DownloadManager
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt


# Modelo de entrada atualizado
class ChatInput(BaseModel):
    question: str
    has_pdf: bool = False  # Flag para indicar se há PDF anexado


# Modelo de saída
class ChatOutput(BaseModel):
    response: str
    pdf_path: str


# Inicializar o FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rota de teste/health check
@app.get("/")
async def root():
    return {"status": "ok"}


# Monta o diretório 'output' para servir arquivos estáticos
app.mount("/static", StaticFiles(directory="output"), name="static")

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configurar a chave da API do Google Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "API Key não encontrada. Certifique-se de que a variável 'GEMINI_API_KEY' está configurada no arquivo .env."
    )

# Configurar a API Key
genai.configure(api_key=api_key)

# Inicializar o gerenciador de downloads
download_manager = DownloadManager()


# Nova rota para gerar token
@app.post("/token", response_model=Dict[str, str])
async def login(credentials: HTTPBasicCredentials):
    """
    Rota para gerar token de acesso.
    Aqui você deve implementar sua própria lógica de validação de usuário.
    Este é apenas um exemplo simplificado.
    """
    # Exemplo simples - você deve implementar sua própria validação
    if credentials.username == "admin" and credentials.password == "senha123":
        token = create_access_token({"sub": credentials.username})
        return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(
        status_code=401,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Atualizar a rota de processamento
@app.post(
    "/chat_with_pdf/",
    response_model=ChatOutput,
    description="Enviar pergunta com PDF opcional",
    dependencies=[Depends(JWTBearer())],
)
async def process_question_with_pdf(
    request: Request,  # Adicionar request para pegar o token
    question: str = Form(...),
    pdf_file: UploadFile = File(None),
):
    try:
        # Extrair user_id do token
        auth_header = request.headers.get("Authorization")
        token = auth_header.split(" ")[1]
        user_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = user_data["sub"]

        if pdf_file is not None and pdf_file != "":
            # Ler o conteúdo do PDF
            pdf_content = await pdf_file.read()
            pdf_text = extract_text_from_pdf(pdf_content)

            # Modificar a pergunta para incluir o contexto do PDF
            enhanced_question = f"""
            Analise o seguinte POP existente e faça as alterações solicitadas:

            POP Atual:
            {pdf_text}

            Alterações solicitadas:
            {question}
            """

            response = chat_with_persona(enhanced_question)
        else:
            # Comportamento padrão sem PDF
            response = chat_with_persona(question)

        response = extract_tex_content(response)
        guard = Guard().use(ValidTex, on_fail="exception")
        guard.validate(response)

        output_directory = "./output"
        os.makedirs(output_directory, exist_ok=True)

        pdf_path = compile_latex(response, output_directory)
        if pdf_path:
            pdf_filename = os.path.basename(pdf_path)

            # Criar token único para download
            download_token = download_manager.create_download_token(
                pdf_filename, user_id
            )

            # URL de download com token
            pdf_download_url = f"http://127.0.0.1:8001/secure_download/{download_token}"
            return {"response": response, "pdf_path": pdf_download_url}
        else:
            raise HTTPException(status_code=500, detail="Falha ao gerar o PDF.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")


# Nova rota para download seguro
@app.get("/secure_download/{token}")
def secure_download(token: str):
    filename = download_manager.validate_token(token)

    if not filename:
        raise HTTPException(
            status_code=403, detail="Token de download inválido ou expirado"
        )

    file_path = os.path.join("./output", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )

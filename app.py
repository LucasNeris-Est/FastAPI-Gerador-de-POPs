from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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


# Nova rota para upload de PDF com modificações
@app.post(
    "/chat_with_pdf/",
    response_model=ChatOutput,
    description="Enviar pergunta com PDF opcional",
)
async def process_question_with_pdf(
    question: str = Form(...), pdf_file: UploadFile = File(None)  # Pode ser None
):
    try:
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
            pdf_download_url = f"http://127.0.0.1:8001/download_pdf/{pdf_filename}"
            return {"response": response, "pdf_path": pdf_download_url}
        else:
            raise HTTPException(status_code=500, detail="Falha ao gerar o PDF.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")


@app.get("/download_pdf/{filename}")
def download_pdf(filename: str):
    file_path = os.path.join("./output", filename)
    if os.path.exists(file_path):
        return FileResponse(
            file_path,
            media_type="application/pdf",
            filename=filename,  # Força o download com o nome original
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    else:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")

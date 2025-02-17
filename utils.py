import os
import re  # Para capturar conteúdo entre delimitadores
import subprocess
import fitz  # PyMuPDF for PDF text extraction
from PyPDF2 import PdfReader
import google.generativeai as genai
from fastapi import HTTPException
from personas import PERSONA_DESCRIPTION_GERAPOP
import json


# Função para extrair conteúdo entre delimitadores
def extract_tex_content(tex_string):
    """
    Extrai o conteúdo entre os delimitadores \documentclass e \end{document}.

    Args:
    - tex_string (str): String contendo o código TeX.

    Returns:
    - str: Conteúdo entre os delimitadores ou mensagem de erro.
    """
    match = re.search(
        r"\\documentclass.*?\\begin\{document\}(.*?)\\end\{document\}",
        tex_string,
        re.DOTALL,
    )
    if match:
        return (
            r"\documentclass"
            + tex_string.split(r"\documentclass", 1)[1].split(r"\begin{document}", 1)[0]
            + r"\begin{document}"
            + match.group(1)
            + r"\end{document}"
        )
    else:
        return "Erro: Delimitadores \\documentclass e \\end{document} não encontrados."


# Gera o PDF a partir do código LaTeX
def compile_latex(tex_content, output_directory):
    """
    Compila o código LaTeX diretamente em PDF usando pdflatex.

    Args:
        tex_content (str): Código LaTeX a ser compilado.
        output_directory (str): Diretório onde o PDF será salvo.

    Returns:
        str: Caminho do arquivo PDF gerado.
    """
    # Caminho do arquivo .tex
    tex_file = os.path.join(output_directory, "document.tex")
    pdf_file = os.path.join(output_directory, "document.pdf")

    # Salvar o conteúdo LaTeX em um arquivo .tex
    with open(tex_file, "w", encoding="utf-8") as file:
        file.write(tex_content)

    try:
        # Ler o caminho do pdflatex do arquivo de configuração
        with open("config.json", "r") as config_file:
            config = json.load(config_file)
            pdflatex_path = config["pdflatex_path"]

        # Executar o pdflatex para compilar o arquivo .tex
        subprocess.run(
            [
                pdflatex_path,
                "-interaction=nonstopmode",
                "document.tex",
            ],
            cwd=output_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        print(f"PDF gerado com sucesso: {pdf_file}")
        return pdf_file

    except subprocess.CalledProcessError as e:
        print("Erro durante a compilação do LaTeX:", e)
        return None

    except FileNotFoundError as e:
        print("Erro: Arquivo de configuração não encontrado.", e)
        return None

    except KeyError as e:
        print(
            "Erro: Caminho do pdflatex não especificado no arquivo de configuração.", e
        )
        return None


# Função para interagir com o Gemini
def chat_with_persona(question):
    """
    Envia uma pergunta para o Gemini e retorna a resposta gerada utilizando a persona GERAPOP.
    """
    try:
        # Inicializar o modelo
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # Criar o prompt com a persona fixa e a pergunta
        prompt = f"{PERSONA_DESCRIPTION_GERAPOP}\n\nPergunta: {question}"

        # Enviar o prompt para o modelo Gemini
        response = model.generate_content(prompt)

        # Retornar a resposta gerada
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o Gemini: {e}")


# Função para extrair texto do PDF
def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extrai texto de um arquivo PDF.
    """
    try:
        # Usando PyMuPDF para melhor extração de texto
        doc = fitz.open(stream=pdf_file, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao processar PDF: {str(e)}")

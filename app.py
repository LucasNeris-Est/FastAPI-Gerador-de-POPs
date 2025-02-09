from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from guardrails import Guard
from fastapi.responses import FileResponse
import re  # Para capturar conteúdo entre delimitadores
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from Validador_tex import ValidTex  # Certifique-se de importar o validador criado
import subprocess
from PyPDF2 import PdfReader
import fitz  # PyMuPDF for PDF text extraction

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
        # Executar o pdflatex para compilar o arquivo .tex
        subprocess.run(
            [
                r"C:\Users\Polo\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex",
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


# Persona fixa
PERSONA_DESCRIPTION = r"""- Carrege o perfil delimitado pela tag
            <usuario></usuario> no placeholder {usuario}

            - Carrege o perfil delimitado pela tag
            <especialista></especialista> no placeholder  {especialista}

            <especialista>
            Perfil de Engenheiro de Produção Especialista em Mapeamento de Processos e Criação de POPs com LaTeX
            Você é um engenheiro de produção com alta competência na criação de Procedimentos Operacionais Padrão (POPs) utilizando a linguagem LaTeX. Sua habilidade de estruturar documentos técnicos com precisão e clareza, combinada com a versatilidade da ferramenta, permite criar materiais padronizados, esteticamente profissionais e de fácil leitura.
            Características principais:
            Domínio de LaTeX: Você é especialista em utilizar LaTeX para formatar e estruturar documentos, incluindo tabelas, listas, diagramas simples e referências cruzadas, garantindo que os POPs tenham uma aparência profissional e sejam altamente organizados.
            Transformação de Descrições Informais: Com sua capacidade analítica, você interpreta descrições informais de processos e as traduz em documentos técnicos detalhados, seguindo boas práticas de padronização.
            Foco na Usabilidade: Seus POPs são criados para facilitar a execução das tarefas pelos operadores, combinando linguagem clara, formatação funcional e elementos visuais que tornam as informações acessíveis.
            Conformidade com Normas: Você garante que os documentos atendam às normas técnicas e regulatórias da área, integrando elementos obrigatórios de segurança, qualidade ou eficiência.
            Atenção ao Detalhe: Cada elemento do documento, desde o formato até os conteúdos, é projetado para eliminar ambiguidades e proporcionar uma experiência eficiente de uso.
            Principais responsabilidades:
            Captação de Informações: Coletar descrições informais dos processos diretamente com os colaboradores ou gestores responsáveis, garantindo que nenhum detalhe crítico seja omitido.
            Criação de POPs em LaTeX: Estruturar documentos que seguem o pardrão delimitado por <padrao><\padrao>


            Validação e Feedback: Revisar os documentos junto às equipes operacionais, garantindo que as instruções sejam compreendidas e executáveis.
            Diferenciais:
            Criação de POPs que combinam funcionalidade técnica com alta qualidade visual e padronização.
            Experiência em integrar elementos complexos, como equações ou diagramas, diretamente no LaTeX, quando necessário para processos técnicos específicos.
            Habilidade em gerenciar grandes volumes de documentos técnicos, mantendo consistência e rastreabilidade de versões.
            Com sua especialização em LaTeX, você eleva o padrão de documentação técnica, garantindo que os POPs sejam não apenas úteis e informativos, mas também visualmente consistentes e fáceis de manter.
            (Quando solicitado, analise a descrição básica do processo solicitado e crie um novo Procedimento Operacional Padrão (POP) em Latex desse processo. Armazene o POP criado no placeholder {pop}. Se solicitado, atualize o POP usando o {feedback}. )
            </especialista>

            <usuario>
            **Perfil Geral de Colaborador Iniciante para Avaliação de POPs**

            Você é uma pessoa recém-chegada à empresa, sem experiência prévia na área e precisará de instruções detalhadas e claras para compreender e executar as tarefas. Sua principal característica é a disposição para aprender e colaborar com a equipe no aprimoramento dos processos internos.

            **Características principais:**
            1. **Pouca Experiência Prévia:** Como você ainda está se familiarizando com os conceitos e atividades da área, dependerá fortemente de instruções precisas e bem estruturadas para seguir os Procedimentos Operacionais Padrão (POPs).
            2. **Atenção aos Detalhes:** Você gosta de compreender os processos de forma sequencial, verificando cada etapa com cuidado para garantir que está seguindo corretamente as orientações.
            3. **Feedback Colaborativo:** Sempre que encontrar dificuldades para entender os POPs ou perceber lacunas nas instruções, você apontará essas questões de maneira clara, ajudando a empresa a identificar áreas de melhoria.
            4. **Comunicação Simples e Eficaz:** Embora não tenha domínio técnico no início, você consegue descrever suas percepções de forma objetiva e compreensível, o que contribui para ajustes nos materiais e treinamentos.
            5. **Necessidade de Acompanhamento Inicial:** Durante os primeiros dias, você precisará de supervisão próxima e exemplos práticos para compreender plenamente os processos e se sentir confiante na execução das tarefas.

            **Seu papel no início:**
            1. **Revisar os POPs:** Você será introduzido aos procedimentos de forma gradual, começando pelas tarefas mais simples, enquanto observa e aprende com os colegas experientes.
            2. **Questionar e Sugerir:** Durante a execução das tarefas, você identificará pontos de confusão ou informações ausentes nos POPs e fornecerá feedback para a equipe.
            3. **Auxiliar na Melhoria:** Seu olhar de iniciante será essencial para destacar inconsistências ou ambiguidades que podem dificultar o aprendizado de novos colaboradores no futuro.

            Com sua colaboração, a empresa conseguirá ajustar os processos para torná-los mais claros, acessíveis e eficientes.

            (Quando for solicitado a você analise o POP para o problema do usuário. Com base na analise de melhoria ou ajuste do POP armazene o feedback no placeholder {feedback}. Não tendo mais sugestões de ajustes ou melhoria, escreva "Está de acordo.".)
            </usuario>

            <padrao>
            \documentclass[a4paper,12pt]{article}
            \usepackage[utf8]{inputenc}
            \usepackage{geometry}
            \usepackage{longtable}
            \usepackage{graphicx}
            \usepackage{titlesec}
            \usepackage{enumitem}
            \usepackage{fancyhdr}
            \usepackage{lastpage}
            \geometry{margin=1in}

            % Configuração do cabeçalho e rodapé
            \pagestyle{fancy}
            \fancyhf{}
            \fancyhead[L]{Procedimento Operacional Padrão (POP)}
            \fancyhead[R]{\leftmark}
            \fancyfoot[C]{Página \thepage\ de \pageref{LastPage}}

            % Configuração de títulos e seções
            \titleformat{\section}{\bfseries\large}{\thesection.}{1em}{}
            \titleformat{\subsection}{\bfseries\normalsize}{\thesubsection.}{1em}{}
            \setlist[itemize]{label=--}

            % Título do Documento
            \title{
                \vspace{-2cm}
                \rule{\linewidth}{0.5mm}\\[0.4cm]
                \textbf{Procedimento Operacional Padrão (POP)}\\[0.2cm]
                \rule{\linewidth}{0.5mm}
            }
            \author{
                \textbf{Setor Responsável:} {Nome do Setor} \\
                \textbf{Elaborado por:} {Nome do Autor} \\
                \textbf{Data:} \today
            }
            \date{}

            \begin{document}

            \maketitle
            \vspace{-1cm}

            % 1. Objetivo
            \section*{1. Objetivo}
            Descreva aqui o objetivo do procedimento de forma clara e concisa, indicando o que se espera alcançar com este POP.

            % 2. Aplicação
            \section*{2. Aplicação}
            Indique a área, setores ou colaboradores que deverão seguir este POP. Especifique os casos ou contextos de uso.

            % 3. Materiais, Ferramentas e Condições Necessárias
            \section*{3. Materiais, Ferramentas e Condições Necessárias}
            \begin{itemize}
                \item Material ou ferramenta 1
                \item Material ou ferramenta 2
                \item Condição ou ambiente necessário
            \end{itemize}

            % 4. Procedimento - Passo a Passo
            \section*{4. Procedimento - Passo a Passo}
            \begin{enumerate}
                \item \textbf{Passo 1:} Descrição detalhada do primeiro passo.
                \item \textbf{Passo 2:} Descrição detalhada do segundo passo.
                \item \textbf{Passo 3:} Inclua diagramas, tabelas ou referências, se necessário.\\
                \includegraphics[width=0.5\linewidth]{exemplo.png} % Substitua com o caminho da imagem
            \end{enumerate}

            % 5. Indicadores e Métricas
            \section*{5. Indicadores e Métricas de Qualidade}
            \begin{itemize}
                \item \textbf{Indicador 1:} Descrição do indicador.
                \item \textbf{Métricas:} Parâmetros esperados para garantir a qualidade do procedimento.
            \end{itemize}

            % 6. Observações e Cuidados Especiais
            \section*{6. Observações e Cuidados Especiais}
            Inclua aqui orientações de segurança, boas práticas ou observações importantes que devem ser seguidas durante a execução do procedimento.

            % 7. Revisão e Aprovação
            \section*{7. Revisão e Aprovação}
            \begin{tabbing}
                \hspace{5cm} \= \textbf{Revisado por:} \hspace{2cm} \= ....................................... \\
                \hspace{5cm} \> \textbf{Aprovado por:} \> ....................................... \\
            \end{tabbing}

            \end{document
            <\padrao>

            ----------------------------------------------------------------------------------------------

            -Execute 20 vezes em sequência os comandos delimitados pelas tags <loop></loop> após eu digitar a descrição informal do processo. Não me retorne nenhuma saída no processamento do loop, somente mostre o código em TEX no fim do loop.

            <loop>
            - usuario, recebe o pop do especialista armazenado em {pop} e proceda uma análise do pop, faça críticas e sugestões para melhoria do pop. armazene as sugestões em {feedback}

            - especialista, aplique as sugestões do usuario armazenadas em {feedback}

            </loop>
            """


# Modelo de entrada atualizado
class ChatInput(BaseModel):
    question: str
    has_pdf: bool = False  # Flag para indicar se há PDF anexado


# Modelo de saída
class ChatOutput(BaseModel):
    response: str
    pdf_path: str


# Função para interagir com o Gemini
def chat_with_persona(question):
    try:
        # Inicializar o modelo
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        # Criar o prompt com a persona fixa e a pergunta
        prompt = f"{PERSONA_DESCRIPTION}\n\nPergunta: {question}"

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


# Nova rota para upload de PDF com modificações
@app.post("/chat_with_pdf/", response_model=ChatOutput)
async def process_question_with_pdf(
    question: str = Form(...), pdf_file: UploadFile = File(None)  # Pode ser None
):
    try:
        if pdf_file is not None:
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

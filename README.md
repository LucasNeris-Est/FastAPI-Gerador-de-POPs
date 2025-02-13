Aqui está o README.md bem formatado e estruturado em Markdown para seu projeto:  

---

```markdown
# 📜 API de Geração de POPs com Autenticação

API desenvolvida em **FastAPI** para geração automatizada de **Procedimentos Operacionais Padrão (POPs)** utilizando **IA generativa (Google Gemini)**.  
O sistema inclui **autenticação JWT**, **geração segura de PDFs** e um **sistema de download com tokens únicos**.

---

## 🚀 Características Principais

✅ Geração de POPs utilizando **IA (Google Gemini)**  
✅ **Autenticação** via JWT  
✅ **Sistema seguro de download** com tokens únicos  
✅ Conversão automática para **PDF via LaTeX**  
✅ Suporte a **upload de PDFs para referência**  

---

## 📋 Pré-requisitos

Antes de instalar e rodar a API, certifique-se de que tem os seguintes requisitos:

- **Python 3.8+**
- **MiKTeX** (ou outro compilador **LaTeX**)
- **Conta Google Cloud** com API **Gemini** ativada
- **Ambiente virtual Python** (recomendado)

---

## 🛠 Instalação

1️⃣ Clone o repositório:
```bash
git clone https://github.com/seu-usuario/api-geracao-pops.git
cd api-geracao-pops
```

2️⃣ Crie e ative um ambiente virtual:
```bash
python -m venv venv
# Para Windows:
venv\Scripts\activate
# Para Linux/MacOS:
source venv/bin/activate
```

3️⃣ Instale as dependências:
```bash
pip install -r requirements.txt
```

4️⃣ Configure as variáveis de ambiente (**.env**):
```plaintext
JWT_SECRET_KEY=sua_chave_secreta_muito_segura
GEMINI_API_KEY=sua_chave_api_gemini
```

5️⃣ Configure o caminho do **pdflatex** no arquivo `config.json`:
```json
{
    "pdflatex_path": "caminho/para/seu/pdflatex"
}
```

---

## 📂 Estrutura do Projeto

```plaintext
.
├── .env                    # Variáveis de ambiente
├── app.py                  # Arquivo principal da aplicação
├── auth.py                 # Sistema de autenticação JWT
├── config.json             # Configurações do projeto
├── download_manager.py     # Gerenciador de downloads
├── requirements.txt        # Dependências do projeto
└── utils.py                # Funções utilitárias
```

---

## ▶️ Como Usar

### 1️⃣ Inicie o servidor:
```bash
uvicorn app:app --reload --port 8001
```

### 2️⃣ Obtenha um token de acesso:
```bash
curl -X POST "http://localhost:8001/token" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "senha123"}'
```

### 3️⃣ Faça uma requisição para gerar um POP:
```bash
curl -X POST "http://localhost:8001/chat_with_pdf/" \
  -H "Authorization: Bearer seu_token_aqui" \
  -F "question=Crie um POP para manutenção de equipamentos" \
  -F "pdf_file=@caminho/do/arquivo.pdf"
```

✅ O sistema retornará uma **URL segura** para download do **PDF gerado**.

---

## 📌 API Endpoints

### 🔑 POST `/token`
Gera um token de acesso.  
**Body**:  
```json
{
  "username": "string",
  "password": "string"
}
```
**Retorno**:  
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

### 📝 POST `/chat_with_pdf/`
Gera um POP baseado na pergunta e PDF opcional.  
**Headers**:
```
Authorization: Bearer {token}
```
**Form Data**:
- `question`: (string) **Obrigatório**
- `pdf_file`: (arquivo) **Opcional**  

**Retorno**:
```json
{
  "response": "string",
  "pdf_path": "string"
}
```

---

### 📥 GET `/secure_download/{token}`
Faz o download do **PDF gerado** usando um **token único**.  
**Parâmetros**:
- `token`: (string) Token de download válido.  

**Retorno**:
- Arquivo **PDF**.

---

## 🔒 Segurança Implementada

✅ **Autenticação JWT** com expiração de **30 minutos**  
✅ **Tokens únicos de download** com expiração de **5 minutos**  
✅ **Uso único** dos tokens de download  
✅ **Validação de arquivos PDF**  
✅ **Sanitização de entrada LaTeX**  

---

## 🤝 Contribuindo

1. **Faça um Fork** do projeto  
2. Crie uma **branch** para sua feature:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Commit** suas mudanças:
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```
4. **Push** para a branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. **Abra um Pull Request** 🚀

---

## ❌ Tratamento de Erros

⚠️ **Tokens inválidos ou expirados**  
⚠️ **Falhas na geração de PDF**  
⚠️ **Erros de compilação LaTeX**  
⚠️ **Uploads de arquivos inválidos**  
⚠️ **Falhas na API do Gemini**  

---

## 📌 Boas Práticas

✔️ Use um **ambiente virtual Python**  
✔️ Mantenha as **dependências atualizadas**  
✔️ **Não compartilhe suas chaves de API**  
✔️ Faça **backup regular** dos dados  
✔️ Monitore os **logs do sistema**  

---

## 📜 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE.md](LICENSE.md) para mais detalhes.

---

## 📬 Suporte

📧 Para dúvidas ou suporte, abra uma **issue** no GitHub ou entre em contato por email:  
📩 **seu-email@exemplo.com**  
```

---

Esse README agora está **mais legível, organizado e bem formatado**, seguindo as boas práticas de documentação em Markdown. 🚀

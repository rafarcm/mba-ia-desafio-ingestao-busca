# Ingestão e Busca Semântica com LangChain e Postgres

## Como executar o projeto

Esta implementação usa o **Google Gemini** para gerar os embeddings e as respostas.

### Pré-requisitos

- **Python 3.12.** Versões mais novas, como a 3.14, não conseguem instalar algumas dependências fixadas no `requirements.txt`.
- **Docker e Docker Compose**, para rodar o PostgreSQL com pgVector.
- **Chave de API do Google Gemini**, que pode ser criada em [Google AI Studio](https://aistudio.google.com/apikey).

### 1. Criar o ambiente virtual e instalar as dependências

Na raiz do projeto:

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Se o seu sistema não tiver o Python 3.12, use o [uv](https://docs.astral.sh/uv/), que baixa essa versão automaticamente:

```bash
uv venv venv --python 3.12
source venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Configurar as variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

Depois, preencha o `.env` com os seus valores. A coluna "Exemplo" mostra valores possíveis, não obrigatórios:

| Variável | Descrição | Exemplo |
|---|---|---|
| `GOOGLE_API_KEY` | Sua chave da API do Gemini. | `AIza...` |
| `GOOGLE_EMBEDDING_MODEL` | Modelo do Gemini que transforma texto em vetores. | `models/gemini-embedding-001` |
| `GOOGLE_LLM_MODEL` | Modelo do Gemini que escreve as respostas. | `gemini-3.5-flash-lite` |
| `DATABASE_URL` | Endereço de conexão com o PostgreSQL. O exemplo corresponde ao banco do `docker-compose.yml`. | `postgresql+psycopg://postgres:postgres@localhost:5432/rag` |
| `PG_VECTOR_COLLECTION_NAME` | Nome da coleção onde os chunks são salvos. Escolha qualquer nome. | `documento_collection` |
| `PDF_PATH` | Caminho do PDF a ser ingerido, relativo à raiz do projeto. | `document.pdf` |

Os modelos disponíveis mudam com frequência. Confira os atuais na [documentação do Gemini](https://ai.google.dev/gemini-api/docs/models).

As variáveis `OPENAI_*` não são usadas nesta implementação e podem ficar vazias.

### 3. Subir o banco de dados

```bash
docker compose up -d
```

Esse comando sobe o PostgreSQL na porta `5432` e ativa a extensão `vector`.

### 4. Fazer a ingestão do PDF

```bash
python src/ingest.py
```

O script lê o PDF, divide o texto em chunks de 1000 caracteres com overlap de 150, gera um embedding para cada chunk e salva tudo no banco. Ao terminar, mostra algo como a linha abaixo, com o nome de coleção que você escolheu:

```
34 páginas lidas, 67 chunks salvos na coleção 'documento_collection'.
```

A ingestão só precisa ser feita uma vez. Se for executada de novo, a coleção é apagada e recriada, sem duplicar dados.

### 5. Iniciar o chat

```bash
python src/chat.py
```

Digite suas perguntas e use `sair` (ou `Ctrl+C`) para encerrar:

```
Faça sua pergunta (digite 'sair' para encerrar):

PERGUNTA: Qual o faturamento da empresa Alfa IA Indústria?
RESPOSTA: R$ 548.789.613,65

PERGUNTA: Qual é a capital da França?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.

PERGUNTA: sair
Até logo!
```

Os comandos dos passos 4 e 5 devem ser executados **a partir da raiz do projeto**, porque o caminho do PDF no `.env` é relativo a ela.

### Estrutura do código

| Arquivo | Responsabilidade |
|---|---|
| `src/ingest.py` | Lê o PDF, divide em chunks, gera os embeddings e salva no PostgreSQL. |
| `src/search.py` | Monta a chain de busca: vetoriza a pergunta, busca os 10 chunks mais relevantes (`k=10`), monta o prompt e chama o Gemini. |
| `src/chat.py` | Interface de linha de comando que recebe as perguntas e mostra as respostas. |

### Problemas comuns

- **`Variável ... não definida no arquivo .env`:** preencha a variável indicada no `.env`.
- **`Erro ao conectar no banco de dados`:** verifique se o banco está rodando com `docker compose ps`.
- **Erro `404` dizendo que o modelo não está disponível:** o Google descontinua modelos com frequência. Escolha outro modelo na [documentação do Gemini](https://ai.google.dev/gemini-api/docs/models) e atualize `GOOGLE_LLM_MODEL` ou `GOOGLE_EMBEDDING_MODEL` no `.env`.
- **Erro de dimensão do vetor depois de trocar o modelo de embeddings:** rode `python src/ingest.py` de novo. A coleção é recriada com a dimensão do novo modelo.
- **Linhas com `grpc` e `POLLER` ao fechar o chat:** é um aviso inofensivo da biblioteca do Google ao encerrar o programa e pode ser ignorado.
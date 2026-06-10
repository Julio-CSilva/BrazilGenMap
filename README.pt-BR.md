# BrazilGenMap

**🌐 Idioma:** [English](README.md) | **Português (BR)**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

Conjunto de ferramentas para minerar e recuperar metadados de sequenciamento
genômico do banco de dados **SRA (Sequence Read Archive)** do NCBI. O foco
principal é identificar dados relacionados a neoplasias e câncer associados a
instituições e pesquisas no Brasil.

---

## 📂 Estrutura do Repositório

- **search_SRA/** — Scripts Python para busca e recuperação de dados.
  - `searchSRA.py` — Faz buscas no NCBI combinando termos de doenças (ex:
    Cancer, Melanoma) com termos de localização/instituições brasileiras. Gera
    um CSV com os resultados.
  - `concat.py` — Processa o CSV do passo anterior para extrair os IDs únicos
    do SRA.
  - `querySRA.py` — Usa o `concat.py` para obter os IDs únicos e consulta a API
    do NCBI para baixar metadados detalhados de cada amostra.
- **results/** — Diretório de saída dos arquivos `.csv` gerados (ignorado pelo git).
- **environment.yml** — Definição do ambiente Conda.
- **.env.example** — Modelo das variáveis de ambiente necessárias.

---

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
Tenha o [Anaconda](https://www.anaconda.com/) ou
[Miniconda](https://docs.conda.io/en/latest/miniconda.html) instalado.

### 2. Clonar o repositório
```bash
git clone https://github.com/Julio-CSilva/BrazilGenMap.git
cd BrazilGenMap
```

### 3. Criar o ambiente Conda
Use o arquivo `environment.yml` para criar o ambiente com todas as dependências
(BioPython, Pandas, etc.):

```bash
conda env create -f environment.yml
conda activate BrazilGenMap
```

### 4. Configurar variáveis de ambiente (`.env`)
Os scripts leem a configuração de um arquivo `.env`. Copie o modelo e preencha
com seus próprios valores:

```bash
cp .env.example .env
```

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `NCBI_EMAIL` | ✅ | E-mail de contato exigido pela API Entrez do NCBI. |
| `NCBI_API_KEY` | ⬜ opcional | Chave da API do NCBI. Aumenta o limite de 3 para 10 requisições/segundo. [Gere a sua aqui](https://www.ncbi.nlm.nih.gov/account/settings/). |
| `OUTPUT_FILE_LIST_SRA` | ✅ | Caminho onde `searchSRA.py` grava os resultados e `concat.py` os lê. |
| `OUTPUT_FILE_LIST_METADATA` | ✅ | Caminho onde `querySRA.py` grava os metadados extraídos. |

Exemplo de `.env`:

```env
NCBI_EMAIL=seu_email@exemplo.com
NCBI_API_KEY=sua_chave_api_ncbi
OUTPUT_FILE_LIST_SRA=results/resultados_busca_sra.csv
OUTPUT_FILE_LIST_METADATA=results/sra_metadata.csv
```

> ⚠️ **Nunca faça commit do arquivo `.env`.** Ele está no `.gitignore` e contém
> sua chave de API pessoal. Caso uma chave seja exposta, revogue-a e gere outra
> nas configurações da sua conta NCBI.

---

## 🛠️ Como Executar

Execute os passos em ordem para obter o fluxo completo dos dados.

### Passo 1 — Buscar IDs no SRA
O `searchSRA.py` combina termos de doença × instituição × organismo e salva os
resultados.

```bash
cd search_SRA
python searchSRA.py
```
**Saída:** um CSV (definido em `OUTPUT_FILE_LIST_SRA`) com as buscas e os IDs
encontrados.

### Passo 2 — Processar IDs e extrair metadados
O `querySRA.py` usa o `concat.py` para obter os IDs únicos e busca seus
metadados.

```bash
python querySRA.py
```
**Saída:** um CSV (definido em `OUTPUT_FILE_LIST_METADATA`) com informações
detalhadas como BioProject, organismo, estratégia de biblioteca, centro
submissor, título do estudo, etc.

### (Opcional) Inspecionar IDs únicos
Para apenas listar os IDs únicos encontrados, sem buscar metadados:

```bash
python concat.py
```

---

## 📋 Detalhes dos Scripts

### `searchSRA.py`
Consulta o banco `sra` via `Bio.Entrez`. Itera sobre as listas `termos_doencas`
e `termos_localizacao` para encontrar submissões brasileiras relevantes. Define
os identificadores `email`, `api_key` e `tool` recomendados pelo NCBI.

### `concat.py`
Lê a saída do passo anterior, separa os IDs agrupados por ponto e vírgula,
remove duplicatas e retorna uma lista limpa de inteiros. Expõe uma única função
`concat()`, podendo ser importado sem efeitos colaterais.

### `querySRA.py`
Script principal de recuperação:
1. Carrega os IDs via `concat.py`.
2. Faz uma requisição `efetch` ao NCBI para cada ID (com timeout de rede e
   controle de taxa).
3. Faz o parsing do XML retornado para extrair atributos específicos.
4. Salva tudo em um CSV consolidado.

---

## 🔐 Segurança e Boas Práticas

- **Segredos fora do git.** As credenciais ficam apenas no `.env`, ignorado
  pelo git. O repositório fornece o modelo `.env.example` no lugar.
- **Controle de taxa.** Os scripts respeitam os limites do NCBI (3 req/s sem
  chave; até 10 req/s com chave) para evitar bloqueios.
- **Timeouts de rede.** As requisições HTTP usam timeout explícito para que uma
  conexão travada não congele a execução.
- **Fonte de dados confiável.** O XML é processado apenas a partir das respostas
  do NCBI. Se adaptar estes scripts para processar XML de fontes não confiáveis,
  considere usar [`defusedxml`](https://pypi.org/project/defusedxml/) para
  mitigar ataques baseados em XML.
- **Apenas dados públicos.** O projeto lida com metadados públicos do SRA;
  nenhum dado de paciente ou identificável é processado.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou um
pull request.

## 📄 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

# BrazilGenMap

Este repositório contém um conjunto de ferramentas para minerar e recuperar metadados de sequenciamento genômico do banco de dados **SRA (Sequence Read Archive)** do NCBI. O foco principal é identificar dados relacionados a neoplasias e câncer associados a instituições e pesquisas no Brasil.

## 📂 Estrutura do Repositório

- **search_SRA/**: Contém os scripts Python para busca e recuperação de dados.
  - `searchSRA.py`: Realiza buscas no NCBI combinando termos de doenças (ex: Cancer, Melanoma) com termos de localização/instituições brasileiras. Gera um arquivo CSV com os resultados.
  - `concat.py`: Processa o CSV gerado pelo script anterior para extrair e identificar IDs únicos do SRA (`id_sra`).
  - `querySRA.py`: Automaticamente roda o script `concat.py` e com o resultado consulta a API do NCBI para baixar metadados detalhados de cada amostra.
- **results/**: Diretório destinado ao armazenamento dos arquivos de saída (`.csv`).
- **environment.yml**: Arquivo de configuração para criação do ambiente Conda.

---

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
Certifique-se de ter o [Anaconda](https://www.anaconda.com/) ou [Miniconda](https://docs.conda.io/en/latest/miniconda.html) instalado em seu sistema.

### 2. Clonar o Repositório
```bash
git clone https://github.com/Julio-CSilva/BrazilGenMap.git
cd BrazilGenMap
```

### 3. Criar o Ambiente Conda
Utilize o arquivo `environment.yml` fornecido para criar o ambiente com todas as dependências necessárias (BioPython, Pandas, etc.).

```bash
conda env create -f environment.yml
```

Ative o ambiente:
```bash
conda activate BrazilGenMap
```

### 4. Configuração de Variáveis de Ambiente (.env)
Para que os scripts funcionem corretamente e tenham acesso à API do NCBI, você deve criar um arquivo `.env` na raiz do projeto ou dentro da pasta `search_SRA` (dependendo de onde executar, mas recomenda-se na raiz para organização), contendo as seguintes chaves:

Crie um arquivo chamado `.env` e adicione:

```env
NCBI_EMAIL=seu_email@exemplo.com
NCBI_API_KEY=sua_chave_api_ncbi
OUTPUT_FILE_LIST_SRA=/caminho/completo/para/BrazilGenMap/results/resultados_busca_sra.csv
OUTPUT_FILE_LIST_METADATE=/caminho/completo/para/BrazilGenMap/results/resultados_metadados.csv
```

> **Nota**: `OUTPUT_FILE_LIST_SRA` define onde o script `searchSRA.py` salvará os resultados iniciais e de onde `concat.py` os lerá. Recomenda-se usar o caminho absoluto ou relativo para a pasta `results`.

---

## 🛠️ Como Executar

A execução deve seguir uma ordem lógica para obter o fluxo completo dos dados.

### Passo 1: Busca de IDs no SRA
O script `searchSRA.py` realiza combinações de termos (Doenças x Instituições Brasileiras) e salva os resultados.

```bash
cd search_SRA
python searchSRA.py
```
**Resultado**: Um arquivo CSV (definido em `OUTPUT_FILE_LIST_SRA`) contendo as buscas e os IDs encontrados.

### Passo 2: Processamento e Extração de Metadados
O script `querySRA.py` utiliza a lógica do `concat.py` para obter os IDs únicos e buscar seus metadados.

 Execute o script:

```bash
python querySRA.py
```

**Resultado**: Um arquivo `sra_metadata.csv` será gerado na pasta `results/` contendo informações detalhadas como Bioproject, Organismo, Data de Publicação, Instituição, etc.

### (Opcional) Verificação de IDs Únicos
Se desejar apenas ver a lista de IDs únicos encontrados sem fazer a busca de metadados, você pode executar o script auxiliar:

```bash
python concat.py
```

---

## 📋 Detalhes dos Scripts

### `searchSRA.py`
Consulta o banco de dados `sra` usando `Bio.Entrez`. Ele itera sobre listas de termos (`termos_doencas` e `termos_localizacao`) para encontrar submissões brasileiras relevantes.

### `concat.py`
Lê o arquivo de saída do passo anterior, separa os IDs (que podem vir agrupados por ponto e vírgula), remove duplicatas e retorna uma lista limpa de inteiros.

### `querySRA.py`
O script principal de recuperação de dados.
1. Carrega os IDs via `concat.py`.
2. Para cada ID, faz uma requisição `efetch` ao NCBI.
3. Faz o parsing do XML retornado para extrair atributos específicos.
4. Salva tudo em um CSV consolidado.
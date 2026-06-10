# BrazilGenMap

**🌐 Language:** **English** | [Português (BR)](README.pt-BR.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20634570.svg)](https://doi.org/10.5281/zenodo.20634570)

A toolkit to mine and retrieve genomic sequencing metadata from NCBI's
**SRA (Sequence Read Archive)** database. Its main goal is to identify
neoplasm- and cancer-related data associated with Brazilian institutions
and research groups.

---

## 📂 Repository Structure

- **search_SRA/** — Python scripts for searching and retrieving data.
  - `searchSRA.py` — Searches NCBI by combining disease terms (e.g. Cancer,
    Melanoma) with Brazilian location/institution terms. Produces a CSV with
    the results.
  - `concat.py` — Processes the CSV from the previous step to extract the
    unique SRA IDs.
  - `querySRA.py` — Uses `concat.py` to obtain the unique IDs and queries the
    NCBI API to download detailed metadata for each sample.
- **results/** — Output directory for the generated `.csv` files (git-ignored).
- **environment.yml** — Conda environment definition.
- **.env.example** — Template for the required environment variables.

---

## 🚀 Installation & Setup

### 1. Prerequisites
Make sure you have [Anaconda](https://www.anaconda.com/) or
[Miniconda](https://docs.conda.io/en/latest/miniconda.html) installed.

### 2. Clone the repository
```bash
git clone https://github.com/Julio-CSilva/BrazilGenMap.git
cd BrazilGenMap
```

### 3. Create the Conda environment
Use the provided `environment.yml` to create the environment with all
dependencies (BioPython, Pandas, etc.):

```bash
conda env create -f environment.yml
conda activate BrazilGenMap
```

### 4. Configure environment variables (`.env`)
The scripts read their configuration from a `.env` file. Copy the template
and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
| --- | --- | --- |
| `NCBI_EMAIL` | ✅ | Contact e-mail required by the NCBI Entrez API. |
| `NCBI_API_KEY` | ⬜ optional | NCBI API key. Raises the rate limit from 3 to 10 requests/second. [Generate one here](https://www.ncbi.nlm.nih.gov/account/settings/). |
| `OUTPUT_FILE_LIST_SRA` | ✅ | Path where `searchSRA.py` writes results and `concat.py` reads them. |
| `OUTPUT_FILE_LIST_METADATA` | ✅ | Path where `querySRA.py` writes the extracted metadata. |

Example `.env`:

```env
NCBI_EMAIL=your_email@example.com
NCBI_API_KEY=your_ncbi_api_key
OUTPUT_FILE_LIST_SRA=results/resultados_busca_sra.csv
OUTPUT_FILE_LIST_METADATA=results/sra_metadata.csv
```

> ⚠️ **Never commit your `.env` file.** It is listed in `.gitignore` and
> contains your personal API key. If a key is ever exposed, revoke and
> regenerate it from your NCBI account settings.

---

## 🛠️ Usage

Run the steps in order to get the full data flow.

### Step 1 — Search SRA IDs
`searchSRA.py` combines disease × institution × organism terms and saves the
results.

```bash
cd search_SRA
python searchSRA.py
```
**Output:** a CSV (defined by `OUTPUT_FILE_LIST_SRA`) with the searches and the
IDs found.

### Step 2 — Process IDs & extract metadata
`querySRA.py` uses `concat.py` to obtain the unique IDs and fetches their
metadata.

```bash
python querySRA.py
```
**Output:** a CSV (defined by `OUTPUT_FILE_LIST_METADATA`) with detailed
information such as BioProject, organism, library strategy, submitting center,
study title, etc.

### (Optional) Inspect unique IDs
To only list the unique IDs found, without fetching metadata:

```bash
python concat.py
```

---

## 📋 Script Details

### `searchSRA.py`
Queries the `sra` database via `Bio.Entrez`. It iterates over the
`termos_doencas` (diseases) and `termos_localizacao` (locations) lists to find
relevant Brazilian submissions. Sets the NCBI `email`, `api_key`, and `tool`
identifiers as recommended by NCBI.

### `concat.py`
Reads the previous step's output, splits semicolon-grouped IDs, drops
duplicates, and returns a clean list of integers. Exposes a single `concat()`
function so it can be imported without side effects.

### `querySRA.py`
The main retrieval script:
1. Loads the IDs via `concat.py`.
2. Sends an `efetch` request to NCBI for each ID (with a network timeout and
   rate-aware throttling).
3. Parses the returned XML to extract specific attributes.
4. Saves everything to a consolidated CSV.

---

## 🔐 Security & Best Practices

- **Secrets stay out of git.** Credentials live only in `.env`, which is
  git-ignored. The repository ships an `.env.example` template instead.
- **Rate limiting.** The scripts respect NCBI's request limits (3 req/s
  without an API key, up to 10 req/s with one) to avoid being throttled or
  blocked.
- **Network timeouts.** HTTP requests use an explicit timeout so a hanging
  connection won't freeze a run.
- **Trusted data source.** XML is parsed only from NCBI responses. If you ever
  adapt these scripts to parse XML from untrusted sources, consider using
  [`defusedxml`](https://pypi.org/project/defusedxml/) to mitigate XML-based
  attacks.
- **Public data only.** This project handles publicly available SRA metadata;
  no patient-level or personally identifiable data is processed.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

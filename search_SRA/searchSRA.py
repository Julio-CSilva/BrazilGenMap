import csv
import time
import os
from dotenv import load_dotenv
from Bio import Entrez


#e-mail para usar a API.
load_dotenv()
Entrez.email = os.getenv("NCBI_EMAIL")
Entrez.api_key = os.getenv("NCBI_API_KEY")  # opcional; aumenta o limite de taxa do NCBI
Entrez.tool = "BrazilGenMap"
DB_TARGET = "sra"
OUTPUT_FILE = os.getenv("OUTPUT_FILE_LIST_SRA")

if not Entrez.email:
    raise EnvironmentError(
        "A variável de ambiente 'NCBI_EMAIL' não está definida. "
        "O NCBI exige um e-mail de contato. Configure-a no arquivo .env."
    )
if not OUTPUT_FILE:
    raise EnvironmentError(
        "A variável de ambiente 'OUTPUT_FILE_LIST_SRA' não está definida. "
        "Configure-a no arquivo .env."
    )

#Garante que o diretório de saída exista antes de escrever.
output_dir = os.path.dirname(OUTPUT_FILE)
if output_dir:
    os.makedirs(output_dir, exist_ok=True)

termos_doencas = [
    'Neoplasms[MeSH Terms]',
    'Cancer[All Fields] OR Tumor[AllFields]',
    'Malignancy[Title/Abstract]',
    'Breast Neoplasms[MeSH Terms]',
    'Lung Neoplasms[MeSH Terms]',
    'Prostatic Neoplasms[MeSH Terms]',
    'Colorectal Neoplasms[MeSH Terms]',
    'Glioblastoma[MeSH Terms]',
    'Leukemia[MeSH Terms]',
    'Lymphoma[MeSH Terms]',
    'Melanoma[MeSH Terms]',
    'Stomach Neoplasms[MeSH Terms]',
    'Ovarian Neoplasms[MeSH Terms]',
    'Metastasis[Title/Abstract]',
    'Oncology[All Fields]'
]

termos_localizacao = [
    'Brazil[All Fields]',

    #PRINCIPAIS INSTITUIÇÕES E HOSPITAIS
    '(INCA OR Instituto Nacional de Cancer)',
    '(A.C.Camargo Cancer Center OR Fundacao Antonio Prudente)',
    '(Hospital de Cancer de Barretos OR Hospital de Amor)',
    '(Hospital Sirio-Libanes)',
    '(Hospital Israelita Albert Einstein)',

    #PRINCIPAIS UNIVERSIDADES DE PESQUISA
    '(Universidade de Sao Paulo OR USP)',
    '(Universidade Estadual de Campinas OR UNICAMP)',
    '(Universidade Federal do Rio de Janeiro OR UFRJ)',
    '(Universidade Federal de Minas Gerais OR UFMG)',
    '(Fiocruz OR Fundacao Oswaldo Cruz)',
    
    #AGÊNCIAS DE FOMENTO
    'FAPESP'
]

termos_organismo = [
    'Homo sapiens[Organism]',
    'txid9606[Organism]'
]

print(f"Iniciando buscas combinadas no banco de dados '{DB_TARGET}'.")
print(f"Os resultados serão salvos em '{OUTPUT_FILE}'.")
total_combinacoes = len(termos_doencas) * len(termos_localizacao) * len(termos_organismo)
combinacao_atual = 0

#Abre o arquivo CSV para escrita
with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    #Escreve o cabeçalho do arquivo
    writer.writerow(['Combinação_Utilizada', 'Quantidade_Resultados', 'IDs_Encontrados'])

    #Loop para criar e testar cada combinação
    for doenca in termos_doencas:
        for local in termos_localizacao:
            for organismo in termos_organismo:
                    combinacao_atual += 1
                    
                    #Monta a query final combinando os termos
                    query = f"{doenca} AND {local} AND {organismo}"
                    
                    print(f"\n[{combinacao_atual}/{total_combinacoes}] Testando: {query}")

                    try:
                        #Executa a busca (esearch) para obter a contagem e a lista de IDs
                        handle = Entrez.esearch(db=DB_TARGET, term=query, retmax=100000) #retmax define o max de IDs a retornar
                        record = Entrez.read(handle)
                        handle.close()

                        count = int(record['Count'])
                        id_list = record['IdList']
                        
                        #Converte a lista de IDs em uma string separada por ponto e vírgula
                        id_list_str = ";".join(id_list)

                        print(f"-> Encontrados: {count} resultados.")

                        #Escreve a linha no arquivo CSV
                        writer.writerow([query, count, id_list_str])

                    except Exception as e:
                        #Em caso de erro na requisição, registra o erro no CSV
                        print(f"!! Ocorreu um erro na requisição: {e}")
                        writer.writerow([query, 0, f"ERRO: {e}"])

                    time.sleep(1)

print(f"\nBusca finalizada com sucesso! Verifique o arquivo '{OUTPUT_FILE}'.")
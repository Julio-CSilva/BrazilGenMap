import csv
import time
import os
from Bio import Entrez

#e-mail para usar a API.
Entrez.email = os.getenv("NCBI_EMAIL")
DB_TARGET = "sra"
OUTPUT_FILE = "resultados_busca_sra.csv"

termos_doencas = [
    '"Neoplasms"[MeSH Terms]',
    '"Cancer"[All Fields] OR "Tumor"[AllFields]',
    '"Malignancy"[Title/Abstract]',

    '"Breast Neoplasms"[MeSH Terms]',
    '"Lung Neoplasms"[MeSH Terms]',
    '"Prostatic Neoplasms"[MeSH Terms]',
    '"Colorectal Neoplasms"[MeSH Terms]',
    '"Glioblastoma"[MeSH Terms]',
    '"Leukemia"[MeSH Terms]',
    '"Lymphoma"[MeSH Terms]',
    '"Melanoma"[MeSH Terms]',
    '"Stomach Neoplasms"[MeSH Terms]',
    '"Ovarian Neoplasms"[MeSH Terms]',
    
    '"Metastasis"[Title/Abstract]',
    '"Oncology"[All Fields]'
]

termos_localizacao = [
    '"Brazil"[All Fields]',

    #--- PRINCIPAIS INSTITUIÇÕES E HOSPITAIS
    '("INCA" OR "Instituto Nacional de Cancer")',
    '("A.C.Camargo Cancer Center" OR "Fundacao Antonio Prudente")',
    '("Hospital de Cancer de Barretos" OR "Hospital de Amor")',
    '("Hospital Sirio-Libanes")',
    '("Hospital Israelita Albert Einstein")',

    #--- PRINCIPAIS UNIVERSIDADES DE PESQUISA
    '("Universidade de Sao Paulo" OR "USP")',
    '("Universidade Estadual de Campinas" OR "UNICAMP")',
    '("Universidade Federal do Rio de Janeiro" OR "UFRJ")',
    '("Universidade Federal de Minas Gerais" OR "UFMG")',
    '("Fiocruz" OR "Fundacao Oswaldo Cruz")',
    
    #--- AGÊNCIAS DE FOMENTO
    '"FAPESP"'
]

termos_organismo = [
    '"Homo sapiens"[Organism]',
    'txid9606[Organism]'
]

#termos_estrategia = [
#    "RNA-Seq[Strategy]",
#    "WGS[Strategy]", #Whole Genome Sequencing
#    "WES[Strategy]", #Whole Exome Sequencing
#    "AMPLICON[Strategy]"
#]

print(f"Iniciando buscas combinadas no banco de dados '{DB_TARGET}'.")
print(f"Os resultados serão salvos em '{OUTPUT_FILE}'.")
total_combinacoes = len(termos_doencas) * len(termos_localizacao) * len(termos_organismo)
combinacao_atual = 0

#Abre o arquivo CSV para escrita
with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    #Escreve o cabeçalho do arquivo
    writer.writerow(['Quantidade_Resultados', 'Combinacao_Utilizada', 'IDs_Encontrados'])

    #Loop para criar e testar cada combinação
    for doenca in termos_doencas:
        for local in termos_localizacao:
            for organismo in termos_organismo:
                    combinacao_atual += 1
                    
                    #Monta a query final combinando os termos
                    query = f"({doenca}) AND ({local}) AND ({organismo}))"
                    
                    print(f"\n[{combinacao_atual}/{total_combinacoes}] Testando: {query}")

                    try:
                        #Executa a busca (esearch) para obter a contagem e a lista de IDs
                        handle = Entrez.esearch(db=DB_TARGET, term=query, retmax=10000) #retmax define o max de IDs a retornar
                        record = Entrez.read(handle)
                        handle.close()

                        count = int(record['Count'])
                        id_list = record['IdList']
                        
                        #Converte a lista de IDs em uma string separada por ponto e vírgula
                        id_list_str = ";".join(id_list)

                        print(f"-> Encontrados: {count} resultados.")

                        #Escreve a linha no arquivo CSV
                        writer.writerow([count, query, id_list_str])

                    except Exception as e:
                        #Em caso de erro na requisição, registra o erro no CSV
                        print(f"!! Ocorreu um erro na requisição: {e}")
                        writer.writerow([0, query, f"ERRO: {e}"])

                    time.sleep(1)

print(f"\nBusca finalizada com sucesso! Verifique o arquivo '{OUTPUT_FILE}'.")
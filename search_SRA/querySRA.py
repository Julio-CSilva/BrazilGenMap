import requests
import concat as qsra
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
import pandas as pd
import time
import os

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

def safe_get_text(element, path, attribute=None):
    """
    encontra um elemento ou atributo de forma segura,
    retornando 'N/A' se não for encontrado, para evitar erros.
    """
    if element is None:
        return 'N/A'
    
    node = element.find(path)
    if node is None:
        return 'N/A'
        
    if attribute:
        return node.get(attribute, 'N/A')
    else:
        return node.text if node.text else 'N/A'

def extract_and_save_sra_metadata(sra_ids):
    """
    Consulta a API do NCBI para cada ID SRA da lista, extrai os metadados
    e salva o resultado em um arquivo CSV.
    """
    if not isinstance(sra_ids, list):
        print("Erro: O input deve ser uma lista de IDs SRA.")
        return
    
    api_key = os.getenv("NCBI_API_KEY")
    if not api_key:
        print(
            "Aviso: A chave 'NCBI_API_KEY' não está definida. As requisições seguirão "
            "sem chave, com limite de taxa menor (3 req/s) imposto pelo NCBI."
        )

    # Sem chave o NCBI permite no máximo 3 req/s; com chave, até 10 req/s.
    request_delay = 0.11 if api_key else 0.34

    all_records = []
    total_ids = len(sra_ids)

    for i, sra_id in enumerate(sra_ids):
        current_id = str(sra_id)
        
        print(f"🔬 Consultando metadados para: {current_id} ({i+1}/{total_ids})...")
        
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        params = {"db": "sra", "id": current_id, "api_key": api_key}

        try:
            response = requests.get(base_url, params=params, timeout=60)
            response.raise_for_status() # Verifica se houve erro na requisição (ex: 404)
            
            root = ET.fromstring(response.content)
            
            for package in root.findall('.//EXPERIMENT_PACKAGE'):
                record = {}
                
                # Informações do Experimento
                record['SRR_Accession'] = safe_get_text(package, './/RUN', attribute='accession')
                record['Experiment_Title'] = safe_get_text(package, './/EXPERIMENT/TITLE')
                record['Design_Description'] = safe_get_text(package, './/DESIGN/DESIGN_DESCRIPTION')
                
                # Descritor da Biblioteca
                record['Library_Name'] = safe_get_text(package, './/LIBRARY_DESCRIPTOR/LIBRARY_NAME')
                record['Library_Strategy'] = safe_get_text(package, './/LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY')
                record['Library_Source'] = safe_get_text(package, './/LIBRARY_DESCRIPTOR/LIBRARY_SOURCE')
                record['Library_Selection'] = safe_get_text(package, './/LIBRARY_DESCRIPTOR/LIBRARY_SELECTION')
                
                # Plataforma de Sequenciamento
                record['Instrument_Model'] = safe_get_text(package, './/PLATFORM/ILLUMINA/INSTRUMENT_MODEL')
                
                # Informações da Submissão
                record['Lab_name'] = safe_get_text(package, './/Organization/Address/Department')
                record['Center_Name'] = safe_get_text(package, './/SUBMISSION', attribute='center_name')
                
                # Informações do Estudo
                bioproject_node = package.find(".//STUDY/IDENTIFIERS/EXTERNAL_ID[@namespace='BioProject']")
                record['BioProject_ID'] = bioproject_node.text if bioproject_node is not None else 'N/A'
                
                record['Study_Title'] = safe_get_text(package, './/STUDY/DESCRIPTOR/STUDY_TITLE')
                record['Study_Abstract'] = safe_get_text(package, './/STUDY/DESCRIPTOR/STUDY_ABSTRACT')

                # Informações da Amostra
                record['Sample_Primary_ID (SRS)'] = safe_get_text(package, './/SAMPLE/IDENTIFIERS/PRIMARY_ID')
                biosample_node = package.find(".//SAMPLE/IDENTIFIERS/EXTERNAL_ID[@namespace='BioSample']")
                record['BioSample_ID (SAMN)'] = biosample_node.text if biosample_node is not None else 'N/A'
                
                record['Taxon_ID'] = safe_get_text(package, './/SAMPLE/SAMPLE_NAME/TAXON_ID')
                record['Scientific_Name'] = safe_get_text(package, './/SAMPLE/SAMPLE_NAME/SCIENTIFIC_NAME')
                
                all_records.append(record)

            time.sleep(request_delay)

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Falha na conexão para o ID {current_id}: {e}")
            continue # Pula para o próximo ID
        except ET.ParseError as e:
            print(f"  ❌ Falha ao processar XML para o ID {current_id}: {e}")
            continue # Pula para o próximo ID
        except Exception as e:
            print(f"  ❌ Ocorreu um erro inesperado para o ID {current_id}: {e}")
            continue # Pula para o próximo ID

    if not all_records:
        print("\nNenhum dado foi encontrado para os IDs fornecidos.")
        return

    df = pd.DataFrame(all_records)
    output_filename = os.getenv("OUTPUT_FILE_LIST_METADATA")
    if not output_filename:
        print("Erro: A variável de ambiente 'OUTPUT_FILE_LIST_METADATA' não está definida.")
        return

    output_dir = os.path.dirname(output_filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    df.to_csv(output_filename, index=False, encoding='utf-8-sig')

    print(f"\n✅ Sucesso! {len(all_records)} registro(s) foram extraídos de {total_ids} IDs consultados.")
    print(f"💾 Os dados foram salvos no arquivo: '{output_filename}'")


if __name__ == "__main__":
    sra_codes = qsra.concat()
    extract_and_save_sra_metadata(sra_codes)
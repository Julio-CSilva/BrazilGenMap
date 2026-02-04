import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
df = pd.read_csv(os.getenv("OUTPUT_FILE_LIST_SRA"))

#Retorna uma lista com todos os IDs SRA únicos encontrados no arquivo de resultados.
def concat():
    list_sra = df['IDs_Encontrados'].str.split(';').explode().dropna().astype(int).unique().tolist()
    return list_sra

print(f"Total unique SRA IDs: {len(concat())}")
print(concat())
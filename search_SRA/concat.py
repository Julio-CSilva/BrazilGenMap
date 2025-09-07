import pandas as pd

df = pd.read_csv("../results/resultados_busca_sra.csv")

def concat():
    list_sra = df['IDs_Encontrados'].str.split(';').explode().dropna().astype(int).unique().tolist()
    return list_sra

print(f"Total unique SRA IDs: {len(concat())}")
print(concat())
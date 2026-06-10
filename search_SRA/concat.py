import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def concat():
    """Retorna uma lista com todos os IDs SRA únicos encontrados no arquivo de resultados."""
    input_file = os.getenv("OUTPUT_FILE_LIST_SRA")
    if not input_file:
        raise EnvironmentError(
            "A variável de ambiente 'OUTPUT_FILE_LIST_SRA' não está definida. "
            "Configure-a no arquivo .env antes de executar."
        )

    df = pd.read_csv(input_file)
    list_sra = (
        df['IDs_Encontrados']
        .str.split(';')
        .explode()
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )
    return list_sra


if __name__ == "__main__":
    unique_ids = concat()
    print(f"Total unique SRA IDs: {len(unique_ids)}")
    print(unique_ids)

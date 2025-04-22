import pandas as pd

def registrar_leitura(codigo_barras, op, quantidade):
    # Registrar a leitura no CSV
    apontamento = {
        "CODIGO_BARRAS": codigo_barras,
        "OP": op,
        "QUANTIDADE": quantidade,
        "DATA_APONTAMENTO": pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')
    }
    df = pd.DataFrame([apontamento])
    df.to_csv('apontamentos.csv', mode='a', header=False, index=False)

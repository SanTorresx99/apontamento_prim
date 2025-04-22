import firebirdsql
import pandas as pd

def carregar_ops(data_input, especie=None, subespécie=None):
    try:
        # Conexão com o banco de dados Firebird
        conn = firebirdsql.connect(
            host='localhost',
            port=3051,  # Porta do Firebird
            database=r'C:/Touchcomp/database_teste/MENTOR.FDB',  # Caminho do banco de dados
            user='SYSDBA',
            password='masterkey'
        )
        cursor = conn.cursor()

        # SQL com os joins e filtragem pelos parâmetros
        sql = f"""
            SELECT
                op.id_os_producao_linha_prod as id_op,
                op.data_prev_inicio as data_op,
                op.codigo,
                p.id_produto,
                p.nome as produto,
                op.quantidade_prev_prod as qtd_prev_prod,
                cb.codigo_barras,
                e.nome as especie,
                se.nome as sub_especie
            FROM os_producao_linha_prod op
            INNER JOIN grade_cor gc ON gc.id_grade_cor = op.id_grade_cor
            INNER JOIN produto_grade pg ON pg.id_produto_grade = gc.id_produto_grade
            INNER JOIN produto p ON p.id_produto = pg.id_produto
            INNER JOIN especie e ON e.id_especie = p.id_especie
            INNER JOIN sub_especie se ON se.id_sub_especie = p.id_sub_especie
            INNER JOIN codigo_barras cb ON cb.id_produto = p.id_produto
            WHERE op.data_prev_inicio = '{data_input}'
        """

        # Adicionando filtros para espécie e subespécie, caso fornecidos
        if especie:
            sql += f" AND e.nome = '{especie}'"
        if subespécie:
            sql += f" AND se.nome = '{subespécie}'"

        # Executar a consulta
        cursor.execute(sql)
        rows = cursor.fetchall()

        # Criar DataFrame a partir dos resultados da consulta
        df = pd.DataFrame(rows, columns=['id_op', 'data_op', 'codigo', 'id_produto', 'produto', 'qtd_prev_prod', 'codigo_barras', 'especie', 'sub_especie'])
        conn.close()
        return df
    except Exception as e:
        print(f"[ERRO] Ao carregar OPs: {e}")
        return pd.DataFrame()

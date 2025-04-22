import pandas as pd
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Importando as funções dos módulos dentro de src/logic
from logic.consulta_ops import carregar_ops  # Importando a função para carregar as OPs do banco
from logic.leitor_codigo import registrar_leitura  # Importando a função para registrar a leitura

# Função para fazer o login
def login():
    # Lógica de login (aqui vamos validar os dados do arquivo CSV)
    username = input("Digite seu usuário: ")
    password = input("Digite sua senha: ")

    # Carregar os usuários do arquivo CSV
    try:
        usuarios_df = pd.read_csv('src/usuarios.csv')  # Caminho do arquivo de usuários
        usuario_valido = usuarios_df[(usuarios_df['usuario'] == username) & (usuarios_df['senha'] == password)]

        if not usuario_valido.empty:
            print(f"Bem-vindo {username}!")
            return username
        else:
            print("Usuário ou senha inválidos.")
            return None
    except Exception as e:
        print(f"[ERRO] Ao carregar usuários: {e}")
        return None

# Função para carregar as OPs filtradas pela data
def carregar_ops(data, especie=None, subespécie=None):
    try:
        # Conexão direta via firebirdsql
        import firebirdsql

        conn = firebirdsql.connect(
            host='localhost',
            port=3051,  # Porta do Firebird
            database=r'C:/Touchcomp/database_teste/MENTOR.FDB',  # Caminho do banco de dados
            user='SYSDBA',
            password='masterkey'
        )

        cursor = conn.cursor()
        sql = f"""
            SELECT op.id_os_producao_linha_prod as id_op, op.data_prev_inicio as data_op, op.codigo,
            p.id_produto, p.nome as produto, op.quantidade_prev_prod as qtd_prev_prod, cb.codigo_barras,
            e.nome as especie, se.nome as sub_especie
            FROM os_producao_linha_prod op
            INNER JOIN grade_cor gc ON gc.id_grade_cor = op.id_grade_cor
            INNER JOIN produto_grade pg ON pg.id_produto_grade = gc.id_produto_grade
            INNER JOIN produto p ON p.id_produto = pg.id_produto
            INNER JOIN especie e ON e.id_especie = p.id_especie
            INNER JOIN sub_especie se ON se.id_sub_especie = p.id_sub_especie
            INNER JOIN codigo_barras cb ON cb.id_produto = p.id_produto
            WHERE op.data_prev_inicio = '{data}'
        """
        cursor.execute(sql)
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=['id_op', 'data_op', 'codigo', 'id_produto', 'produto', 'qtd_prev_prod', 'codigo_barras', 'especie', 'sub_especie'])
        conn.close()
        return df
    except Exception as e:
        print(f"[ERRO] Ao carregar OPs: {e}")
        return pd.DataFrame()

# Função para registrar a leitura de um produto
def registrar_leitura(codigo_barras, op, quantidade):
    try:
        # Registrar a leitura no CSV
        apontamento = {
            "CODIGO_BARRAS": codigo_barras,
            "OP": op,
            "QUANTIDADE": quantidade,
            "DATA_APONTAMENTO": pd.to_datetime('now').strftime('%Y-%m-%d %H:%M:%S')
        }
        df = pd.DataFrame([apontamento])
        df.to_csv('src/apontamentos.csv', mode='a', header=False, index=False)  # Salvando os apontamentos no CSV
        print(f"Leitura registrada com sucesso para o código de barras: {codigo_barras}")
    except Exception as e:
        print(f"[ERRO] Ao registrar a leitura: {e}")

# Função principal
def main():
    print("=== SISTEMA DE APONTAMENTO DE PRODUÇÃO ===")

    # Login do usuário
    username = login()

    if username:  # Caso o login seja válido
        while True:
            data = input("Informe a data da OP (YYYY-MM-DD ou 'sair' para encerrar): ")
            if data.lower() == 'sair':
                print("Saindo...")
                break  # Finaliza o programa

            # Carregar as OPs para a data informada
            ops = carregar_ops(data)
            if ops.empty:
                print("Nenhuma OP encontrada para esta data.")
                continue

            print("OPs disponíveis:")
            # Exibindo as OPs como um menu numerado
            for idx, row in ops.iterrows():
                print(f"[{idx+1}] {row['produto']} - {row['qtd_prev_prod']} unidades previstas")

            # Menu de opções para filtro de espécie
            print("\n=== ESPÉCIE DISPONÍVEIS ===")
            especies = ops['especie'].unique()
            for idx, especie in enumerate(especies, 1):
                print(f"[{idx}] {especie}")
            print("[0] Pular filtro de espécie")

            especie_escolhida = int(input("Selecione uma espécie ou 0 para pular: "))
            if especie_escolhida != 0:
                especie_selecionada = especies[especie_escolhida - 1]
                print(f"Espécie selecionada: {especie_selecionada}")
                ops = ops[ops['especie'] == especie_selecionada]

            # Menu de opções para filtro de subespécie
            print("\n=== SUBESPÉCIE DISPONÍVEIS ===")
            subespecies = ops['sub_especie'].unique()
            for idx, subesp in enumerate(subespecies, 1):
                print(f"[{idx}] {subesp}")
            print("[0] Pular filtro de subespécie")

            subesp_escolhida = int(input("Selecione uma subespécie ou 0 para pular: "))
            if subesp_escolhida != 0:
                subesp_selecionada = subespecies[subesp_escolhida - 1]
                print(f"Subespécie selecionada: {subesp_selecionada}")
                ops = ops[ops['sub_especie'] == subesp_selecionada]

            # Menu de opções para selecionar a OP
            print("\n=== OPs disponíveis após filtro ===")
            for idx, row in ops.iterrows():
                print(f"[{idx+1}] {row['produto']} - {row['qtd_prev_prod']} unidades previstas")

            op_escolhida = input("Escolha o número da OP ou '0' para pular: ")
            if op_escolhida == '0':
                print("Operação ignorada.")
                continue

            try:
                op_escolhida = int(op_escolhida) - 1
                if op_escolhida < 0 or op_escolhida >= len(ops):
                    print("Opção inválida, tente novamente.")
                    continue

                op_data = ops.iloc[op_escolhida]
                codigo_barras = input(f"Digite o código de barras para a OP {op_data['produto']}: ")
                quantidade = int(input("Digite a quantidade do produto: "))
                registrar_leitura(codigo_barras, op_data['id_op'], quantidade)
            except ValueError:
                print("Opção inválida, tente novamente.")
    else:
        print("Usuário ou senha inválidos.")

if __name__ == "__main__":
    main()
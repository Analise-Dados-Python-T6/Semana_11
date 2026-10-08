import psycopg2
import pandas as pd

try:
    connection = psycopg2.connect(
        host='localhost',
        dbname='postgres',
        user='alvarohenriquecartanopimentel',
        password='',
        port=5432
    )

except Exception as e:
    print(f"""
    Erro ao conectar ao banco de dados:
    
    {e.__class__.__name__}

    {e}
    """)
    exit(1)  # incluí esta linha para parar a execução do programa caso a conexão falhe!

# finally:
    # print("Oi!")

cursor = connection.cursor()

cursor.execute("SELECT version();")
db_version = cursor.fetchall()

print("\n")

print("Conexão bem-sucedida!")
print(f"Versão do Banco: {db_version[0]}")

print("\n")


do_script = input(
    "Deseja executar o script de criação de tabelas e inserção de dados? (s/n): ").strip().lower() == 's'
script = """

-- ================================================================
-- POSTGRESQL
-- ================================================================

-- ----------------------------------------------------------------
-- ESTRUTURA
-- ----------------------------------------------------------------

DROP TABLE IF EXISTS clientes;
CREATE TABLE clientes (
    id             INTEGER PRIMARY KEY,
    nome           VARCHAR(80)  NOT NULL,
    email          VARCHAR(120) NOT NULL,
    segmento       VARCHAR(20)  NOT NULL,
    data_cadastro  DATE         NOT NULL
);

DROP TABLE IF EXISTS transacoes;
CREATE TABLE transacoes (
    id          INTEGER PRIMARY KEY,
    cliente_id  INTEGER NOT NULL,
    data        DATE NOT NULL,
    valor       NUMERIC(10,2),
    status      VARCHAR(15) NOT NULL
);

DROP TABLE IF EXISTS itens_transacao;
CREATE TABLE itens_transacao (
    id             INTEGER PRIMARY KEY,
    transacao_id   INTEGER NOT NULL,
    produto        VARCHAR(40) NOT NULL,
    quantidade     INTEGER NOT NULL,
    preco_unitario NUMERIC(10,2) NOT NULL,

    FOREIGN KEY (transacao_id)
        REFERENCES transacoes(id)
);

DROP TABLE IF EXISTS passageiros;
CREATE TABLE passageiros (
    id             INTEGER PRIMARY KEY,
    nome           VARCHAR(80)  NOT NULL,
    email          VARCHAR(120) NOT NULL,
    telefone       VARCHAR(20)  NOT NULL,
    data_cadastro  DATE         NOT NULL
);

DROP TABLE IF EXISTS motoristas;
CREATE TABLE motoristas (
    id             INTEGER PRIMARY KEY,
    nome           VARCHAR(80) NOT NULL,
    data_cadastro  DATE        NOT NULL,
    nota           NUMERIC(3,2)
);

DROP TABLE IF EXISTS corridas;
CREATE TABLE corridas (
    id             INTEGER PRIMARY KEY,
    passageiro_id  INTEGER NOT NULL,
    motorista_id   INTEGER NOT NULL,
    data_hora      TIMESTAMP NOT NULL,
    valor          NUMERIC(8,2) NOT NULL,

    FOREIGN KEY (passageiro_id)
        REFERENCES passageiros(id),

    FOREIGN KEY (motorista_id)
        REFERENCES motoristas(id)
);


-- ----------------------------------------------------------------
-- CLIENTES: 200 linhas
-- ----------------------------------------------------------------

INSERT INTO clientes (
    id,
    nome,
    email,
    segmento,
    data_cadastro
)
WITH RECURSIVE n AS (
    SELECT 1 AS i

    UNION ALL

    SELECT i + 1
    FROM n
    WHERE i < 200
)
SELECT
    i,
    'Cliente ' || LPAD(i::TEXT, 3, '0'),
    'cliente' || i || '@' ||
    CASE 1 + (i % 4)
        WHEN 1 THEN 'gmail.com'
        WHEN 2 THEN 'outlook.com'
        WHEN 3 THEN 'empresa.com.br'
        WHEN 4 THEN 'yahoo.com'
    END,
    CASE 1 + (i % 4)
        WHEN 1 THEN 'Varejo'
        WHEN 2 THEN 'Premium'
        WHEN 3 THEN 'Corporate'
        WHEN 4 THEN 'Startup'
    END,
    DATE '2023-01-01'
        + ((i * 7) % 700) * INTERVAL '1 day'
FROM n;


-- ----------------------------------------------------------------
-- TRANSACOES: 1200 linhas
-- ----------------------------------------------------------------

INSERT INTO transacoes (
    id,
    cliente_id,
    data,
    valor,
    status
)
WITH RECURSIVE n AS (
    SELECT 1 AS i

    UNION ALL

    SELECT i + 1
    FROM n
    WHERE i < 1200
)
SELECT
    i,
    CASE
        WHEN i % 60 = 0 THEN 9001
        ELSE 1 + ((i * 13) % 190)
    END,
    DATE '2024-01-01'
        + ((i * 11) % 639) * INTERVAL '1 day',
    CASE
        WHEN i % 50 = 7 THEN NULL
        ELSE ROUND(
            (
                20
                + ((i * 37) % 481)
                + ((i % 100)::NUMERIC / 100)
            )::NUMERIC,
            2
        )
    END,
    CASE 1 + (i % 10)
        WHEN 1 THEN 'concluida'
        WHEN 2 THEN 'concluida'
        WHEN 3 THEN 'concluida'
        WHEN 4 THEN 'concluida'
        WHEN 5 THEN 'concluida'
        WHEN 6 THEN 'concluida'
        WHEN 7 THEN 'pendente'
        WHEN 8 THEN 'pendente'
        WHEN 9 THEN 'cancelada'
        WHEN 10 THEN 'estornada'
    END
FROM n;


-- ----------------------------------------------------------------
-- Plantio das transações duplicadas
--
-- MySQL:
-- UPDATE transacoes t
-- JOIN transacoes o ON o.id = t.id - 190
-- SET t.valor = o.valor
-- WHERE t.id BETWEEN 390 AND 394;
--
-- PostgreSQL:
-- UPDATE ... FROM ...
-- ----------------------------------------------------------------

UPDATE transacoes AS t
SET valor = o.valor
FROM transacoes AS o
WHERE o.id = t.id - 190
  AND t.id BETWEEN 390 AND 394;


-- ----------------------------------------------------------------
-- ITENS_TRANSACAO
-- 1 a 3 itens por transação para as transações 1..400
-- ----------------------------------------------------------------

INSERT INTO itens_transacao (
    id,
    transacao_id,
    produto,
    quantidade,
    preco_unitario
)
WITH RECURSIVE n AS (
    SELECT 1 AS i
    UNION ALL
    SELECT i + 1
    FROM n
    WHERE i < 400
),
k AS (
    SELECT 1 AS j
    UNION ALL SELECT 2
    UNION ALL SELECT 3
)
SELECT
    (n.i - 1) * 3 + k.j,
    n.i,
    CASE 1 + ((n.i + k.j) % 5)
        WHEN 1 THEN 'Plano Basico'
        WHEN 2 THEN 'Plano Plus'
        WHEN 3 THEN 'Suporte'
        WHEN 4 THEN 'Consultoria'
        WHEN 5 THEN 'Treinamento'
    END,
    1 + ((n.i * k.j) % 3),
    ROUND(
        (
            10
            + ((n.i * 7 + k.j * 13) % 90)
        )::NUMERIC,
        2
    )
FROM n
JOIN k
    ON k.j <= 1 + (n.i % 3);


-- ----------------------------------------------------------------
-- PASSAGEIROS: 150 linhas
-- ----------------------------------------------------------------

INSERT INTO passageiros (
    id,
    nome,
    email,
    telefone,
    data_cadastro
)
WITH RECURSIVE n AS (
    SELECT 1 AS i
    UNION ALL
    SELECT i + 1
    FROM n
    WHERE i < 150
),
base AS (
    SELECT
        i,
        'passageiro' || i || '@' ||
        CASE
            WHEN FLOOR(
                1 + 5 * POWER(
                    ((i * 37) % 151)::NUMERIC / 151,
                    1.7
                )
            ) = 1
                THEN 'gmail.com'
            WHEN FLOOR(
                1 + 5 * POWER(
                    ((i * 37) % 151)::NUMERIC / 151,
                    1.7
                )
            ) = 2
                THEN 'hotmail.com'
            WHEN FLOOR(
                1 + 5 * POWER(
                    ((i * 37) % 151)::NUMERIC / 151,
                    1.7
                )
            ) = 3
                THEN 'outlook.com'

            WHEN FLOOR(
                1 + 5 * POWER(
                    ((i * 37) % 151)::NUMERIC / 151,
                    1.7
                )
            ) = 4
                THEN 'yahoo.com.br'
            ELSE 'uol.com.br'
        END AS em
    FROM n
)
SELECT
    i,
    'Passageiro ' || LPAD(i::TEXT, 3, '0'),
    CASE
        WHEN i % 4 = 0
            THEN UPPER(em)
        WHEN i % 6 = 0
            THEN '  ' || em || ' '
        WHEN i % 10 = 0
            THEN UPPER(LEFT(em, 1)) || SUBSTRING(em FROM 2)
        ELSE em
    END,
    '(21) 9'
        || LPAD(((i * 7919) % 10000)::TEXT, 4, '0')
        || '-'
        || LPAD(((i * 104729) % 10000)::TEXT, 4, '0'),
    DATE '2023-06-01'
        + ((i * 5) % 600) * INTERVAL '1 day'
FROM base;


-- ----------------------------------------------------------------
-- MOTORISTAS: 40 linhas
-- ----------------------------------------------------------------

INSERT INTO motoristas (
    id,
    nome,
    data_cadastro,
    nota
)
WITH RECURSIVE n AS (
    SELECT 1 AS i
    UNION ALL
    SELECT i + 1
    FROM n
    WHERE i < 40
)
SELECT
    i,
    'Motorista ' || LPAD(i::TEXT, 2, '0'),
    DATE '2019-01-01'
        + ((i * 97) % 2400) * INTERVAL '1 day',
    CASE
        WHEN i % 9 = 0 THEN NULL
        ELSE ROUND(
            (
                3.5
                + ((i * 7) % 15)::NUMERIC / 10
            ),
            2
        )
    END
FROM n;


-- ----------------------------------------------------------------
-- CORRIDAS: 3000 linhas
-- ----------------------------------------------------------------

INSERT INTO corridas (
    id,
    passageiro_id,
    motorista_id,
    data_hora,
    valor
)
WITH RECURSIVE n AS (
    SELECT 1 AS i
    UNION ALL
    SELECT i + 1
    FROM n
    WHERE i < 3000
)
SELECT
    i,
    1 + ((i * 17) % 150),
    1 + FLOOR(
        40 * POWER(
            ((i * 7919) % 10007)::NUMERIC / 10007,
            1.6
        )
    )::INTEGER,
    TIMESTAMP '2024-01-01 00:00:00'
        + ((i * 7919) % (639 * 24 * 60))
          * INTERVAL '1 minute',
    ROUND(
        (
            8
            + ((i * 53) % 1400)::NUMERIC / 10
            + (i % 10) * 0.5
        ),
        2
    )
FROM n;
"""
if do_script:
    cursor.execute(script)
    print("\nScript de criação de tabelas e inserção de dados executado com sucesso!\n")

    connection.commit()


do_verify = input(
    "Deseja executar a verificação da base? (s/n): ").strip().lower() == 's'
conferencia_sql = """

-- ----------------------------------------------------------------
-- CONFERÊNCIA FINAL
-- ----------------------------------------------------------------

SELECT
    'clientes' AS tabela,
    COUNT(*) AS linhas
FROM clientes
UNION ALL
SELECT
    'transacoes',
    COUNT(*)
FROM transacoes
UNION ALL
SELECT
    'itens_transacao',
    COUNT(*)
FROM itens_transacao
UNION ALL
SELECT
    'passageiros',
    COUNT(*)
FROM passageiros
UNION ALL
SELECT
    'motoristas',
    COUNT(*)
FROM motoristas
UNION ALL
SELECT
    'corridas',
    COUNT(*)
FROM corridas;

"""
if do_verify:
    try:
        cursor.execute(conferencia_sql)
        conferencia_final = cursor.fetchall()

        conf_final_df = pd.DataFrame(conferencia_final)
        # conf_final_df = pd.DataFrame( conferencia_final, columns=['Tabela', 'Linhas'])

        print(conf_final_df)
    except Exception as e:
        print(f"""
        Erro ao executar a verificação da base:
        
        {e.__class__.__name__}

        {e}
        """)


corridas_por_cliente = """
SELECT cli.nome,
cli.segmento,
sum(trans.valor)
FROM transacoes trans
INNER JOIN clientes cli
ON cli.id = trans.cliente_id
GROUP BY cli.nome, cli.segmento
ORDER BY cli.nome
LIMIT 10
;
"""

cursor.execute(corridas_por_cliente)
resultado = cursor.fetchall()

for nome, segmento, total in resultado:
    print(f"Nome: {nome}, Segmento: {segmento}, Total: {total}")
print("\n")


df = pd.DataFrame(resultado, columns=['Nome', 'Segmento', 'Total'])
print(df)


cursor.close()
connection.close()

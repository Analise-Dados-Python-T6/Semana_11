"""
SQLALCHEMY ORM - SETUP E CONFIGURAÇÃO INICIAL
===============================================

Neste arquivo, você aprenderá a:
1. Importar as bibliotecas necessárias
2. Configurar a conexão com o PostgreSQL
3. Criar a base declarativa do SQLAlchemy
4. Definir classes ORM mapeadas para tabelas do banco

Material preparado para estudantes iniciantes em ORM e SQLAlchemy.
"""

import psycopg
from sqlalchemy import create_engine, text, Column, Integer, String, Date, Numeric, ForeignKey, func
from sqlalchemy.orm import declarative_base, Session
import pandas as pd

print("✓ Importações realizadas com sucesso!")


# Configurações de conexão com o banco PostgreSQL
DB_USER = "alvarohenriquecartanopimentel"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "postgres"

# String de conexão (DSN - Data Source Name)
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print(
    f"String de conexão: postgresql://{DB_USER}:****@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Criar engine (motor de conexão com o banco)
engine = create_engine(DATABASE_URL, echo=True)

print("✓ Engine criada com sucesso!")


# print("\nTestando conexão com o banco...")

# Criar uma sessão (session = conexão ativa com o banco)
session = Session(engine)


# sql = text("SELECT * FROM clientes")

# df = pd.read_sql(sql, engine)

# print("\n")
# print(df)


# classe base será herdada por todos os modelos ORM
Base = declarative_base()

print("✓ Base declarativa criada com sucesso!")


class Cliente(Base):
    """
    Mapeamento da tabela 'clientes' para uma classe Python.

    Cada instância desta classe representa uma linha da tabela clientes.
    Cada atributo de classe representa uma coluna da tabela.
    """

    __tablename__ = "clientes"  # Nome da tabela no banco de dados

    # Definição das colunas (atributos)
    id = Column(Integer, primary_key=True)                  # Chave primária
    nome = Column(String(80), nullable=False)
    email = Column(String(120), nullable=False)
    segmento = Column(String(20), nullable=False)
    data_cadastro = Column(Date, nullable=False)            # DATE NOT NULL

    def __repr__(self):
        """Representação textual do objeto (útil para debug)"""
        return f"<Cliente(id={self.id}, nome='{self.nome}', email='{self.email}', segmento='{self.segmento}')>"


class Transacao(Base):
    """
    Mapeamento da tabela 'transacoes' para uma classe Python.

    Esta tabela tem uma relação com a tabela 'clientes' através da chave estrangeira cliente_id.
    """

    __tablename__ = "transacoes"  # Nome da tabela no banco de dados

    # Definição das colunas
    id = Column(Integer, primary_key=True)                  # Chave primária
    cliente_id = Column(Integer, ForeignKey("clientes.id"),
                        nullable=False)  # Chave estrangeira
    data = Column(Date, nullable=False)                     # DATE NOT NULL
    # NUMERIC(10,2) NULL
    valor = Column(Numeric(10, 2), nullable=True)
    # VARCHAR(15) NOT NULL
    status = Column(String(15), nullable=False)

    def __repr__(self):
        """Representação textual do objeto"""
        return f"<Transacao(id={self.id}, cliente_id={self.cliente_id}, valor={self.valor}, status='{self.status}')>"


print("\nCriando tabelas no banco de dados...")

# Cria todas as tabelas definidas em Base.metadata
Base.metadata.create_all(engine)

print("✓ Tabelas criadas com sucesso!")


try:
    # Executar uma query simples para verificar se está funcionando
    resultado = session.query(Cliente).first()
    # resultado = session.query(Cliente).all()

    if resultado is None:
        print("✓ Conexão OK! (Tabela clientes ainda está vazia)")
    else:
        print(f"✓ Conexão OK! Primeiro cliente encontrado: {resultado}")

except Exception as e:
    print(f"✗ Erro ao conectar: {e}")
    print("Verifique as credenciais e se o PostgreSQL está rodando.")

# finally:
#     session.close()

print("\n\n")
top_3 = session.query(Cliente.nome, func.sum(Transacao.valor).label('total')).join(Transacao).group_by(
    Cliente.id, Cliente.nome).order_by(func.sum(Transacao.valor).desc()).limit(8).all()

for nome, total in top_3:
    print(f"{nome}: R$ {float(total):.2f}")

print("\n\n")

session.close()

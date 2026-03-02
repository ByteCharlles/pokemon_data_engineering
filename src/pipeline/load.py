import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from src.infrastructure.database import db_connector
from src.utils.logger import logger
import os

class DataLoader:
    def __init__(self):
        self.conn_params = {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT")
        }

    def load_pokemons_to_db(self, df: pd.DataFrame):
        if df is None or df.empty:
            logger.error("❌ DataFrame vazio.")
            return False

        # 1. Preparar os dados para inserção em lote (lista de tuplas)
        columns = df.columns.tolist()
        values = [tuple(x) for x in df.to_numpy()]
        
        # 2. Montar a query dinâmica de Upsert
        col_names = ', '.join([f'"{col}"' for col in columns])
        
        # Cria a string de atualização para o ON CONFLICT, ignorando a coluna 'Id' (chave primária)
        update_clause = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in columns if col != 'Id'])
        
        query = f"""
            INSERT INTO pokemons ({col_names})
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                {update_clause}
        """

        # 3. Executar no banco
        try:
            conn = psycopg2.connect(**self.conn_params)
            cursor = conn.cursor()
            
            logger.info("⏳ Realizando Upsert em lote no PostgreSQL...")
            
            execute_values(cursor, query, values)
            
            conn.commit()
            logger.success("✅ Carga (Upsert) finalizada com sucesso!")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro no Upsert: {e}")
            return False

    def load_combats_to_db(self, df: pd.DataFrame):
        """Carrega os combates no PostgreSQL de forma otimizada."""
        if df is None or df.empty: return False
        
        try:
            logger.info(f"⏳ Carregando {len(df)} combates no banco...")
            df.to_sql(
                name='combats',
                con=db_connector.get_engine(),
                if_exists='replace',
                index=False,
                chunksize=10000, 
                method='multi'
            )
            logger.success("✅ Combates carregados com sucesso no PostgreSQL!")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao carregar combates: {e}")
            return False
        
loader = DataLoader()
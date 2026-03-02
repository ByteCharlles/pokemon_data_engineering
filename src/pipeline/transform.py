import os
import pandas as pd
from datetime import datetime
from src.utils.logger import logger

class DataTransformer:
    def __init__(self):
        self.bronze_path = "data/bronze"
        self.silver_path = "data/silver"

    def transform_pokemons(self):
        """Lê da Bronze, aplica transformações e salva na Silver."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        bronze_file = os.path.join(self.bronze_path, date_str, "pokemon_details.json")

        if not os.path.exists(bronze_file):
            logger.error(f"❌ Arquivo bruto não encontrado: {bronze_file}")
            return None

        logger.info("🧹 Iniciando limpeza dos dados (Silver Layer)...")
        
        df = pd.read_json(bronze_file).copy()

        df['name'] = df['name'].str.strip()
        
        # Extrai número da geração
        df["generation"] = (
            df["generation"]
            .astype(str)
            .str.extract(r'(\d+)')
            .astype(int)
        )
        
        # Converte 'legendary' para booleano
        df['legendary'] = df['legendary'].astype(str).str.lower() == 'true'
        
        # Padroniza separador de tipos
        df["types"] = df["types"].str.split("/")
        df["types"] = df["types"].apply(lambda x: ", ".join(x) if isinstance(x, list) else x)
        
        # Converte atributos de combate para numérico
        num_cols = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']
        for col in num_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Cria métrica derivada
        df["total_stats"] = (
            df["hp"] + df["attack"] + df["defense"] + 
            df["sp_attack"] + df["sp_defense"] + df["speed"]
        )
        
        # Salva dados na camada Silver (CSV e Parquet)
        target_dir = os.path.join(self.silver_path, date_str)
        os.makedirs(target_dir, exist_ok=True)
        
        silver_file_csv = os.path.join(target_dir, "pokemons_cleaned.csv")
        df.to_csv(silver_file_csv, index=False, encoding="utf-8")          
        
        silver_file_parquet = os.path.join(target_dir, "pokemons_cleaned.parquet")
        df.to_parquet(silver_file_parquet, index=False)    
        
        logger.info(f"💾 Dados limpos salvos em: {silver_file_parquet}")
        return df

    def transform_combats(self, raw_data):
        """Limpa e formata os dados de combates."""
        logger.info("🧹 Transformando dados de Combates...")
        df = pd.DataFrame(raw_data)
        
        # Converte colunas de ID para numérico e remove nulos
        cols = ['first_pokemon', 'second_pokemon', 'winner']
        for col in cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df = df.dropna().astype(int)
        return df

transformer = DataTransformer()
import os
import pandas as pd
from datetime import datetime
from src.infrastructure.database import db_connector
from src.utils.logger import logger

class GoldLayer:
    def __init__(self):
        self.engine = db_connector.get_engine()
        self.gold_path = "data/gold"

    def process_gold_layer(self):
        logger.info("🥇 Iniciando processamento da Camada Gold (Analytics)...")
        
        try:
            # 1. Lê os dados limpos (Silver) do banco
            df_pokemons = pd.read_sql("SELECT * FROM pokemons", self.engine)
            df_combats = pd.read_sql("SELECT * FROM combats", self.engine)
            
            # 2. Calcula total de vitórias por Pokémon
            vitorias = df_combats['winner'].value_counts().reset_index()
            vitorias.columns = ['id', 'vitorias']
            
            # 3. Calcula total de batalhas disputadas
            batalhas_first = df_combats['first_pokemon'].value_counts()
            batalhas_second = df_combats['second_pokemon'].value_counts()
            total_batalhas = batalhas_first.add(batalhas_second, fill_value=0).reset_index()
            total_batalhas.columns = ['id', 'total_batalhas']
            
            # 4. Junta as estatísticas de combate
            df_stats = pd.merge(total_batalhas, vitorias, on='id', how='left').fillna(0)
            
            # 5. Calcula a Taxa de Vitória (%)
            df_stats['taxa_vitoria'] = (df_stats['vitorias'] / df_stats['total_batalhas']) * 100
            
            # 6. Enriquece as estatísticas com os atributos do Pokémon
            df_gold = pd.merge(df_pokemons, df_stats, on='id', how='inner')
            
            # 6.5 Aplica a tradução e formatação das colunas para Analytics
            df_gold = df_gold.rename(columns={
                'id': 'Id',
                'name': 'Nome',
                'hp': 'Hp',
                'attack': 'Ataque',
                'defense': 'Defesa',
                'sp_attack': 'Ataque Especial',
                'sp_defense': 'Defesa Especial',
                'speed': 'Velocidade',
                'generation': 'Geração',
                'legendary': 'Lendário',
                'types': 'Tipos',
                'total_stats': 'Status Total',
                'total_batalhas': 'Total de Batalhas',
                'vitorias': 'Vitórias',
                'taxa_vitoria': 'Taxa de Vitória'
            })
            
            # 7 SALVAMENTO FÍSICO (CSV e PARQUET) ---
            date_str = datetime.now().strftime("%Y-%m-%d")
            target_dir = os.path.join(self.gold_path, date_str)
            os.makedirs(target_dir, exist_ok=True)

            # Salvando em CSV
            gold_file = os.path.join(target_dir, "gold_pokemon_stats.csv")
            df_gold.to_csv(gold_file, index=False, encoding="utf-8")
            logger.info(f"💾 Gold salva em CSV: {gold_file}")

            # Salvando em Parquet (PyArrow)
            gold_file = os.path.join(target_dir, "gold_pokemon_stats.parquet")
            df_gold.to_parquet(gold_file, engine='pyarrow', index=False)
            logger.info(f"💾 Gold salva em Parquet: {gold_file}")
            
            # 8. Salva a tabela final (Gold) no banco de dados
            df_gold.to_sql('gold_pokemon_stats', self.engine, if_exists='replace', index=False)
            
            logger.success(f"✅ Camada Gold concluída! Tabela 'gold_pokemon_stats' gerada com {len(df_gold)} Pokémons.")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar a camada Gold: {e}")
            return False

gold_processor = GoldLayer()
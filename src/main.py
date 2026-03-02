import sys
from src.utils.logger import logger
from src.infrastructure.database import db_connector
from src.infrastructure.api_client import api_client
from src.pipeline.extract import extractor 
from src.pipeline.transform import transformer
from src.pipeline.load import loader
from src.pipeline.gold import gold_processor

def main():
    logger.info("🚀 Iniciando Pipeline de Dados Pokémon")

    # --- ETAPA 1: Infraestrutura (Banco de Dados) ---
    logger.info("--- ETAPA 1: Validando Conexão com PostgreSQL ---")
    if not db_connector.test_connection():
        logger.critical("❌ Falha crítica: Não foi possível conectar ao banco. Abortando.")
        sys.exit(1)
    
    # --- ETAPA 2: Autenticação (JWT) ---
    logger.info("--- ETAPA 2: Autenticação na API ---")
    token = api_client.get_token()
    if not token:
        logger.error("❌ Falha na autenticação. Verifique as credenciais no .env")
        sys.exit(1)

    # --- ETAPA 3: Extração (Bronze Layer) ---
    logger.info("--- ETAPA 3: Extração de Dados Brutos ---")
    
    raw_data = extractor.extract_all(
        endpoint="pokemon",     # Endpoint da API
        key_name="pokemons"     # Chave de iteração do JSON
    )
    
    if not raw_data:
        logger.warning("⚠️ Nenhum Pokémon retornado na extração básica.")
        sys.exit(1)

    logger.success(f"✅ Lista básica extraída: {len(raw_data)} registros salvos na Bronze.")

    # --- ETAPA 3.1: Extração de Detalhes dos Pokémons ---
    logger.info("--- ETAPA 3.1: Extração de Detalhes dos Pokémons ---")

    detailed_data = extractor.extract_pokemon_details(raw_data)
    
    if raw_data:
        logger.success(f"✅ Extração concluída: {len(raw_data)} registros obtidos e salvos na Bronze.")
    else:
        logger.warning("⚠️ Nenhum dado retornado na extração.")

    # --- ETAPA 4: Transformação (Silver Layer) ---
    logger.info("--- ETAPA 4: Transformação e Limpeza ---")
    df_pokemons = transformer.transform_pokemons()
    
    if df_pokemons is not None:
        logger.success(f"✅ Transformação concluída: Tabela com {df_pokemons.shape[0]} linhas e {df_pokemons.shape[1]} colunas.")
    else:
        logger.warning("⚠️ Falha na transformação.")
    
    # --- ETAPA 5: Processamento de Combates ---
    logger.info("--- ETAPA 5: Extração e Carga de Combates ---")
    
    # Recupera cache local ou extrai via API
    raw_combats = extractor.get_existing_data("combats")
    if not raw_combats:
        raw_combats = extractor.extract_all(endpoint="combats", key_name="combats")
        
    if raw_combats:
        df_combats = transformer.transform_combats(raw_combats)
        loader.load_combats_to_db(df_combats)
    else:
        logger.warning("⚠️ Nenhum combate para processar.")
    
    # --- ETAPA 6: Carga de Pokemons no Banco de Dados ---
    logger.info("--- ETAPA 6: Carga de Pokémons no Banco de Dados ---")
    if df_pokemons is not None:
        loader.load_pokemons_to_db(df_pokemons)
    else:
        logger.warning("⚠️ Não há dados transformados para carregar no banco.")
        
    # --- ETAPA 7: Carga (Gold Layer / Analytics) ---
    logger.info("--- ETAPA 7: Carga no Banco e Análises ---")
    gold_processor.process_gold_layer()    

    logger.success("✨ Pipeline Completo finalizado com sucesso!")        

if __name__ == "__main__":
    # Tratamento global de exceções da pipeline
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("🛑 Execução interrompida manualmente pelo usuário (Ctrl+C).")
    except Exception as e:
        logger.exception(f"💥 Ocorreu um erro inesperado durante o pipeline: {e}")
        sys.exit(1)
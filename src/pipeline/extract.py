import os
import json
import time
from datetime import datetime
from src.infrastructure.api_client import api_client
from src.utils.logger import logger

class DataExtractor:
    def __init__(self):
        self.base_path = "data/bronze"
        os.makedirs(self.base_path, exist_ok=True)

    def save_to_json(self, data, filename):
        """Salva os dados brutos em formato JSON na pasta bronze."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        folder = os.path.join(self.base_path, date_str)
        os.makedirs(folder, exist_ok=True)
        
        file_path = os.path.join(folder, f"{filename}.json")
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info(f"💾 Ficheiro salvo em: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"❌ Erro ao salvar JSON: {e}")
            return None

    def extract_all(self, endpoint, key_name):
        """Extrai todas as páginas de um endpoint e retorna uma lista única."""
        all_records = []
        page = 1
        per_page = 50 

        logger.info(f"📡 Iniciando extração total de: /{endpoint}")
        
        while True:
            params = {"page": page, "per_page": per_page}
            response = api_client.fetch_data(endpoint, params=params)
            
            if not response:
                break
                
            records = response.get(key_name, [])
            if not records:
                break
                
            all_records.extend(records)
            
            total = response.get("total", 0)
            logger.info(f"📥 Página {page}: Obtidos {len(all_records)} de {total}")
            
            
            if len(all_records) >= total or len(records) < per_page:
                break
                
            page += 1
            
            time.sleep(0.5)

        self.save_to_json(all_records, endpoint)
        return all_records

    def extract_pokemon_details(self, basic_pokemons: list):
        """Busca os atributos detalhados de cada Pokémon na API."""
        detailed_pokemons = []
        total = len(basic_pokemons)

        logger.info(f"🔍 Iniciando extração de detalhes para {total} Pokémons. Isso pode levar alguns minutos...")

        for index, poke in enumerate(basic_pokemons):
            poke_id = poke.get("id")
            if not poke_id:
                continue

            
            details = api_client.fetch_data(f"pokemon/{poke_id}")

            if details:
                detailed_pokemons.append(details)
            else:
                logger.warning(f"⚠️ Falha ao buscar detalhes do Pokémon ID {poke_id}")

            
            if (index + 1) % 50 == 0:
                logger.info(f"⏳ Progresso: {index + 1}/{total} Pokémons detalhados...")

           
            time.sleep(0.1)

        
        self.save_to_json(detailed_pokemons, "pokemon_details")
        return detailed_pokemons   

    def get_existing_data(self, filename):
        """Verifica se o arquivo JSON já existe hoje e retorna os dados."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(self.base_path, date_str, f"{filename}.json")
        
        if os.path.exists(file_path):
            logger.info(f"♻️ Arquivo '{filename}.json' encontrado. Carregando dados locais...")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"❌ Erro ao ler arquivo local {file_path}: {e}")
                return None
        return None 
        
extractor = DataExtractor()
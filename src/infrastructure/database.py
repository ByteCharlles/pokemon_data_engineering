from sqlalchemy import create_engine, text  
from sqlalchemy.exc import SQLAlchemyError
from src.config.settings import settings
from src.utils.logger import logger

class DatabaseConnector:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL,pool_pre_ping=True)

    def get_engine(self):
        return self.engine

    def test_connection(self):
        try:
            with self.engine.connect() as connection:
                query = text("SELECT 1") 
                connection.execute(query)
                
                logger.info("✅ Conexão com o PostgreSQL estabelecida com sucesso!")
                return True
        except SQLAlchemyError as e:
            logger.error(f"❌ Erro ao conectar no banco de dados: {e}")
            return False

# Instancia para uso global
db_connector = DatabaseConnector()

if __name__ == "__main__":
    db_connector.test_connection()
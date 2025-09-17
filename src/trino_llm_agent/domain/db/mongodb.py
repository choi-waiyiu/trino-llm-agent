from mongoengine import connect, disconnect, ConnectionFailure
from trino_llm_agent.settings import settings
from loguru import logger

class MongoDBConnector:
    
    @classmethod
    def connect(self):
        try:
            connect(db=settings.DATABASE_NAME, host=settings.DATABASE_HOST, port=settings.DATABASE_PORT)
        except ConnectionFailure as e:
            logger.error(f"MongoDB connection to {settings.DATABASE_HOST} failed: {e!s}")
            raise
        logger.info(f"MongoDB connection to {settings.DATABASE_HOST} succeeded")
    
    @classmethod
    def disconnect(self):
        disconnect()

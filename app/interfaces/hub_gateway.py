from abc import ABC, abstractmethod
from app.entities.processed_agent_data import ProcessedAgentData
import psycopg2

class HubGateway(ABC):
    @abstractmethod
    def save_data(self, processed_data: ProcessedAgentData) -> bool:
        pass

class HubGatewayImplementation(HubGateway):
    def __init__(self, db_config):
        self.db_config = db_config

    def save_data(self, processed_data: ProcessedAgentData) -> bool:
        try:
            logging.error("-----------------------INSIDE save_data --------------------.")
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()

            insert_query = 'INSERT INTO processed_agent_data (road_state) VALUES (%s)'
            cursor.execute(insert_query, (processed_data.road_state,))

            conn.commit()
            cursor.close()
            conn.close()

            return True
        except Exception as e:
            print(f"Помилка при збереженні даних: {e}")
            return False

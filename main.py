
import logging
from app.adapters.agent_mqtt_adapter import AgentMQTTAdapter
from app.adapters.hub_http_adapter import HubHttpAdapter
from app.adapters.hub_mqtt_adapter import HubMqttAdapter

from config import (
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
    MQTT_TOPIC,
    HUB_URL,
    HUB_MQTT_BROKER_HOST,
    HUB_MQTT_BROKER_PORT,
    HUB_MQTT_TOPIC,
)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log"),
        ],
    )

    hub_adapter = HubMqttAdapter(
        broker=HUB_MQTT_BROKER_HOST,
        port=HUB_MQTT_BROKER_PORT,
        topic=HUB_MQTT_TOPIC,
    )

    agent_adapter = AgentMQTTAdapter(
        broker_host=MQTT_BROKER_HOST,
        broker_port=MQTT_BROKER_PORT,
        topic="agend_data_for_lab_4",
        hub_gateway=hub_adapter,
    )

    def on_message(client, userdata, msg):
        
        agent_data = AgentData.from_message(msg.payload)
        processed_data = process_agent_data(agent_data, hub_adapter)
        logging.info(f"Processed data: {processed_data}")
    
    logging.error("-----------------------INSIDE __main__ --------------------.")
    agent_adapter.set_on_message_callback(on_message)

    try:
        agent_adapter.connect()
        agent_adapter.start()
        while True:
            pass
    except KeyboardInterrupt:
        agent_adapter.stop()
        logging.info("System stopped.")
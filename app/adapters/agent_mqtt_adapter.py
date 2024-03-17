import logging
import json
import paho.mqtt.client as mqtt
from app.interfaces.agent_gateway import AgentGateway
from app.entities.agent_data import AgentData, GpsData
from app.usecases.data_processing import process_agent_data
from app.interfaces.hub_gateway import HubGateway


class AgentMQTTAdapter(AgentGateway):
    def __init__(
        self,
        broker_host,
        broker_port,
        topic,
        hub_gateway: HubGateway,
        batch_size=10,
    ):
        self.batch_size = batch_size
        # MQTT
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topic = topic
        self.client = mqtt.Client()
        # Hub
        self.hub_gateway = hub_gateway

    def set_on_message_callback(self, callback):
        logging.info("---------------------------------------set_on_message_callback")
        self.client.on_message = callback

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("---------------------------------------Connected to MQTT broker")
            self.client.subscribe(self.topic)
        else:
            logging.info(f"---------------------------------------Failed to connect to MQTT broker with code: {rc}")

    def on_message(self, client, userdata, msg):
        
        logging.info("--------------- on_message start ---------------")
        logging.info(f"Received message on topic {msg.topic}: {msg.payload}")

        try:
            payload = msg.payload.decode("utf-8")
            logging.info(f"Decoded payload: {payload}")

            logging.info("Validating payload with AgentData model...")
            agent_data = AgentData.model_validate_json(payload, strict=True)
            logging.info(f"Validation successful. AgentData: {agent_data}")

            logging.info("Processing agent data...")
            processed_data = process_agent_data(agent_data)
            logging.info(f"Processed data: {processed_data}")

            logging.info("Saving processed data to the database...")
            if not self.hub_gateway.save_data(processed_data):
                logging.error("Failed to save data to the hub. Hub might be unavailable.")

            logging.info("Processed data saved successfully.")
            
        except Exception as e:
            logging.error(f"Error occurred during MQTT message processing: {e}")

        logging.info("--------------- on_message end ---------------")


    def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_host, self.broker_port, 60)

    def start(self):
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()


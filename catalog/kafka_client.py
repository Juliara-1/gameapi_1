# catalog/kafka_client.py
from django.conf import settings
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
import json
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class KafkaManager:
    @classmethod
    def get_config(cls):
        """Получаем конфиг Kafka с fallback значениями"""
        return getattr(settings, 'KAFKA_CONFIG', {
            'bootstrap_servers': 'localhost:9092',
            'search_topic': 'search_topic',
            'response_topic': 'response_topic'
        })

@lru_cache(maxsize=None)
def get_kafka_producer():
    """Кэшированный продюсер для повторного использования"""
    config = KafkaManager.get_config()
    return KafkaProducer(
        bootstrap_servers=config['bootstrap_servers'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        acks='all',
        retries=3,
        request_timeout_ms=10000
    )

@lru_cache(maxsize=None)
def get_kafka_consumer(group_id='catalog_group'):
    """Кэшированный консьюмер с возможностью указания group_id"""
    config = KafkaManager.get_config()
    return KafkaConsumer(
        bootstrap_servers=config['bootstrap_servers'],
        auto_offset_reset='earliest',
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        consumer_timeout_ms=10000,
        group_id=group_id
    )

class KafkaProducerClient:
    def __init__(self):
        self.producer = get_kafka_producer()

    def send_message(self, topic, value):
        try:
            future = self.producer.send(topic, value=value)
            future.get(timeout=10)
            logger.debug(f"Message sent to {topic}: {str(value)[:100]}...")
            return True
        except KafkaError as e:
            logger.error(f"Kafka producer error: {str(e)}")
            raise

class KafkaConsumerClient:
    def __init__(self, group_id='catalog_group'):
        self.consumer = get_kafka_consumer(group_id)

    def consume_message(self, topic, timeout=10.0):
        self.consumer.subscribe([topic])
        start_time = time.time()
        
        try:
            for message in self.consumer:
                if time.time() - start_time > timeout:
                    logger.warning(f"Timeout consuming from {topic}")
                    return None
                if message.value:
                    logger.debug(f"Received message from {topic}")
                    return message.value
        except KafkaError as e:
            logger.error(f"Kafka consumer error: {str(e)}")
            raise
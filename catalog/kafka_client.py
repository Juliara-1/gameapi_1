import json
import time
from confluent_kafka import Consumer, Producer, KafkaError, KafkaException



class KafkaProducerClient:
    def __init__(self, bootstrap_servers='kafka:9092'):
        self.producer = Producer({
            'bootstrap.servers': bootstrap_servers,
        })

    def send_message(self, topic, message_data):
        """Отправить сообщение в Kafka."""
        self.producer.produce(topic, value=message_data)
        self.producer.flush()


class KafkaConsumerClient:
    def __init__(self, bootstrap_servers='kafka:9092', group_id='django_group'):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
        })

    def consume_message(self, topic, timeout=10):
        """Получить сообщение из Kafka."""
        self.consumer.subscribe([topic])
        start_time = time.time()
        while time.time() - start_time < timeout:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    raise KafkaException(msg.error())
            return json.loads(msg.value().decode('utf-8'))
        return None

    def close(self):
        """Закрыть потребителя Kafka."""
        self.consumer.close()
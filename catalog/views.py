# views.py
import os
import json
import time
import logging
import uuid

from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import SearchQuerySerializer
from .cache import RedisCache
from .kafka_client import KafkaConsumerClient, KafkaProducerClient

logger = logging.getLogger(__name__)

class SearchQueryView(APIView):
    KAFKA_TOPIC = 'search_topic'
    RESPONSE_TOPIC = 'response_topic'

    def __init__(self):
        self.cache = RedisCache()
        self.kafka_producer = KafkaProducerClient()
        self.kafka_consumer = KafkaConsumerClient()


    @swagger_auto_schema(request_body=SearchQuerySerializer)
    def post(self, request):
        serializer = SearchQuerySerializer(data=request.data)

        if serializer.is_valid():
            try:
                query = serializer.validated_data['query']
                request_id = str(uuid.uuid4())
                
                cache_key = f"search_query_{query}"
                logger.info(f"Checking cache for key: {cache_key}")

                cached_result = self.cache.get(cache_key)
                logger.info(f"Cached result: {cached_result}")

                if cached_result:
                    return Response(
                        {
                            'message': 'Search query processed successfully (from cache)',
                            'data': cached_result,
                            'cache': True
                        },
                        status=status.HTTP_200_OK
                    )

                # Отправляем запрос в Kafka
                message_data = json.dumps({
                    'query': query,
                    'request_id': request_id
                })

                logger.info(f"Sending message to Kafka: {message_data}")
                self.kafka_producer.send_message(topic=self.KAFKA_TOPIC, message_data=message_data)

                # Ожидаем ответа от FastAPI
                response_message = self.kafka_consumer.consume_message(self.RESPONSE_TOPIC, timeout=10)
                self.kafka_consumer.close()

                if response_message and response_message.get('request_id') == request_id:
                    # Сохраняем результат в кеш
                    self.cache.set(cache_key, response_message, timeout=3600)  # Кешируем на 1 час
                    return Response(
                        {
                            'message': 'Search query processed successfully',
                            'data': response_message
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {'error': 'No response received from FastAPI'},
                        status=status.HTTP_504_GATEWAY_TIMEOUT
                    )

            except Exception as e:
                logger.error(f"Error processing search query: {e}")
                return Response(
                    {'error': f'Failed to process search query: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

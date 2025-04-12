import json
import time
import logging
import uuid
from catalog.serializers import SearchQuerySerializer, ProviderSerializer, GameSerializer, SearchQueryInputSerializer
from django.http import JsonResponse
from rest_framework import viewsets
from .models import Provider, Game
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from .kafka_client import KafkaProducerClient, KafkaConsumerClient
from drf_yasg.utils import swagger_auto_schema

logger = logging.getLogger(__name__)

class SearchQueryView(APIView):
    def __init__(self):
        super().__init__()
        self.kafka_config = settings.KAFKA_CONFIG
        self._init_kafka_clients()
    
    def _init_kafka_clients(self):
        """Инициализация клиентов с обработкой ошибок и fallback"""
        try:
            self.producer = KafkaProducerClient()
            self.consumer = KafkaConsumerClient(
                group_id='search_query_group'  # Уникальный group_id для этого consumer
            )
        except Exception as e:
            # Fallback: можно использовать заглушки или альтернативные механизмы
            self.producer = None
            self.consumer = None

    @swagger_auto_schema(
        request_body=SearchQueryInputSerializer,
        responses={
            200: "Успешный поиск",
            400: "Неверные параметры запроса",
            503: "Сервис поиска недоступен"
        },
        operation_description="Поиск игр по запросу с использованием Kafka и кеширования",
        tags=['Поиск']
    )
    def post(self, request):
        if not self.producer or not self.consumer:
            return Response(
                {'error': 'Kafka service unavailable'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        serializer = SearchQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data['query']
        cache_key = f"search:{query}"
        
        # Проверка кэша
        if cached := cache.get(cache_key):
            return Response({
                'message': 'Result from cache',
                'data': cached,
                'cache': True
            })
  
        # Отправка в Kafka
        request_id = str(uuid.uuid4())
        message = {
            'query': query,
            'request_id': request_id,
            'timestamp': time.time()
        }
        try:
            self.producer.send_message(
                topic=self.kafka_config['search_topic'],
                value=message
            )
            
            # Ожидание ответа
            response = self.consumer.consume_message(
                topic=self.kafka_config['response_topic'],
                timeout=10.0
            )
            
            if response and response.get('request_id') == request_id:
                cache.set(cache_key, response['data'], self.CACHE_TTL)
                return Response({
                    'message': 'Result from Kafka',
                    'data': response['data'],
                    'cache': False
                })
            
            return Response(
                {'error': 'Timeout waiting for response'},
                status=status.HTTP_504_GATEWAY_TIMEOUT
            )
            
        except Exception as e:
            error_prefix = "Kafka Service Error: "
            error_message = f"{error_prefix}Search service temporary unavailable. Reason: {str(e)}"
    
            # Логирование полной ошибки с traceback
            logger.exception(error_message)
            return Response(
                {'error': 'Search service temporary unavailable'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

def test_cache(request):
    cache_key = 'test_cache'
    data = cache.get(cache_key)
    
    if not data:
        data = {'time': time.time(), 'message': 'Данные закэшированы!'}
        cache.set(cache_key, data, timeout=30)  # Кэш на 30 секунд
        data['message'] = 'Данные только что созданы!'
    
    return JsonResponse(data)

@cache_page(60 * 5)  # Кэш на 5 минут
def game_list(request):
    games = Game.objects.all()
    
@api_view(['GET'])
def test_cache_view(request):
    # Получаем уникальный параметр или генерируем случайное значение
    unique_id = request.query_params.get('id', str(uuid.uuid4()))
    
    # Используем уникальный ключ кэша для каждого запроса с id
    cache_key = f'test_cache_{unique_id}'
    cached_data = cache.get(cache_key)
    
    # Добавляем временную метку для отслеживания актуальности
    current_time = time.time()
    
    if cached_data:
        return Response({
            'data': cached_data,
            'source': 'cache',
            'request_time': current_time,
            'cache_id': unique_id,
            'message': 'Данные получены из кэша'
        })
    else:
        new_data = {
            'timestamp': current_time,
            'content': 'Тестовые данные для кэширования'
        }
        
        cache.set(cache_key, new_data, timeout=30)
        
        return Response({
            'data': new_data,
            'source': 'generated',
            'request_time': current_time,
            'cache_id': unique_id,
            'message': 'Данные только что созданы и сохранены в кэш'
        })

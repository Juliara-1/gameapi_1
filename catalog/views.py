import json
import time
import logging
import uuid
from rest_framework import viewsets
from .models import Provider, Game
from .serializers import ProviderSerializer, GameSerializer
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

logger = logging.getLogger(__name__)

class SearchQueryView(APIView):
    KAFKA_TOPIC = 'search_topic'
    RESPONSE_TOPIC = 'response_topic'
    CACHE_TTL = 60 * 60 * 24  # 24 часа

    def __init__(self):
        # Инициализация Kafka клиентов (реализуйте ваш Kafka клиент)
        self.kafka_producer = KafkaProducerClient()
        self.kafka_consumer = KafkaConsumerClient()

    def post(self, request):
        serializer = SearchQuerySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            query = serializer.validated_data['query']
            cache_key = f"search:{query}"
            
            # Проверка кэша
            cached_result = cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache hit for query: {query}")
                return Response({
                    'message': 'Result from cache',
                    'data': cached_result,
                    'cache': True
                }, status=status.HTTP_200_OK)

            # Если нет в кэше - отправляем в Kafka
            request_id = str(uuid.uuid4())
            message = {
                'query': query,
                'request_id': request_id
            }
            
            self.kafka_producer.send_message(
                topic=self.KAFKA_TOPIC,
                value=json.dumps(message).encode('utf-8')
            )

            # Ожидаем ответ
            response = self.kafka_consumer.consume(
                topics=[self.RESPONSE_TOPIC],
                timeout=10.0
            )
            
            if response and response['request_id'] == request_id:
                # Сохраняем в кэш
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
            logger.error(f"Search error: {str(e)}")
            return Response(
                {'error': str(e)},
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

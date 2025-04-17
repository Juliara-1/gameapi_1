import logging
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .models import Game, Provider
from .serializers import SearchQueryInputSerializer, GameSerializer, ProviderSerializer

logger = logging.getLogger(__name__)

class SearchQueryView(APIView):
    CACHE_TTL = 1  # Кэширование на 1 сек
    @swagger_auto_schema(
        request_body=SearchQueryInputSerializer,
        responses={
            200: "Успешный поиск",
            400: "Неверные параметры запроса"
        },
        operation_description="Поиск игр и провайдеров по запросу"
    )
    def post(self, request):
        # Валидация входных данных
        serializer = SearchQueryInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        query = serializer.validated_data['query'].lower()
        cache_key = f"search_{query}"

        # Проверка кэша
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Returning cached results for query: {query}")
            return Response({
                "message": "Results from cache",
                "data": cached_data,
                "cache": True
            })

        # Поиск в базе данных
        try:
            games = Game.objects.filter(title__icontains=query)
            providers = Provider.objects.filter(name__icontains=query)

            result = {
                "games": GameSerializer(games, many=True).data,
                "providers": ProviderSerializer(providers, many=True).data
            }

            # Сохранение в кэш
            cache.set(cache_key, result, self.CACHE_TTL)
            logger.info(f"New search results cached for query: {query}")

            return Response({
                "message": "Results from database",
                "data": result,
                "cache": False
            })

        except Exception as e:
            logger.error(f"Search error for query '{query}': {str(e)}")
            return Response(
                {"error": "Search service temporary unavailable"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
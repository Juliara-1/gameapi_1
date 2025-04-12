from rest_framework import serializers
from .models import Provider, Game

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = '__all__'  # Все поля модели

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'
class SearchQueryInputSerializer(serializers.Serializer):
    query = serializers.CharField(
        required=True,
        help_text="Поисковый запрос (минимум 2 символа)",
        min_length=2
    )
    # Добавьте другие параметры, если нужно
    limit = serializers.IntegerField(
        required=False,
        default=10,
        help_text="Лимит результатов",
        min_value=1
    )     
class SearchQuerySerializer(serializers.Serializer):
    query = serializers.CharField(
        max_length=255,
        required=True,
        help_text="Поисковый запрос"
    )
    
    # Опционально: можно добавить дополнительные поля
    # Например, фильтры или параметры поиска
    filters = serializers.JSONField(
        required=False,
        help_text="Дополнительные фильтры поиска"
    )
    
    def validate_query(self, value):
        """Дополнительная валидация поискового запроса"""
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Поисковый запрос должен содержать минимум 2 символа")
        return value
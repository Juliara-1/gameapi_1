from rest_framework import serializers
from .models import Game, Provider

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'price', 'is_published']

class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['id', 'name', 'email']

class SearchQueryInputSerializer(serializers.Serializer):
    query = serializers.CharField(
        required=True,
        min_length=2,
        help_text="Поисковый запрос (минимум 2 символа)"
    )

    def validate_query(self, value):
        return value.strip().lower()
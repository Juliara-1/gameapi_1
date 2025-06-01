from rest_framework import serializers
from .models import Game, Provider, SearchQuery


class ProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provider
        fields = ['id', 'name']


class GameSerializer(serializers.ModelSerializer):
    features = ProviderSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'name', 'is_active', 'created_at', 'providers']


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ['query',]
from rest_framework import viewsets
from .models import Provider, Game
from .serializers import ProviderSerializer, GameSerializer

class ProviderViewSet(viewsets.ModelViewSet):
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

# Create your views here.

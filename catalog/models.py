from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Provider(models.Model):
    name = models.CharField(max_length=100)  # Название компании
    email = models.EmailField(default="no-email@example.com")             # Контактный email

    def __str__(self):
        return self.name

class Game(models.Model):
    title = models.CharField(max_length=200)      # Название игры
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)  # Связь с провайдером
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Цена
    is_published = models.BooleanField(default=True)  # Опубликована ли игра

    def __str__(self):
        return f"{self.title} ({self.provider.name})"
@receiver(post_save, sender=Game)
def clear_game_cache(sender, instance, **kwargs):
    cache.delete('game_list_cache_key') 
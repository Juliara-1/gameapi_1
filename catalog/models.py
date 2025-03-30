from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=100)  # Название компании
    email = models.EmailField()             # Контактный email

    def __str__(self):
        return self.name

class Game(models.Model):
    title = models.CharField(max_length=200)      # Название игры
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)  # Связь с провайдером
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Цена
    is_published = models.BooleanField(default=True)  # Опубликована ли игра

    def __str__(self):
        return f"{self.title} ({self.provider.name})"

from django.db import models

class Provider(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(default="no-email@example.com")

    def __str__(self):
        return self.name

class Game(models.Model):
    title = models.CharField(max_length=200)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.provider.name})"
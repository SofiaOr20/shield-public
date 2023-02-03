from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

from api.forms import Choices


class Store(models.Model):
    cod = models.CharField(unique=True, max_length=15)
    accept = ArrayField(models.IntegerField(blank=True, null=True), blank=True, null=True)
    send = ArrayField(models.IntegerField(blank=True, null=True), blank=True, null=True)
    address = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.cod


class Car(models.Model):
    cod = models.CharField(unique=True, max_length=15)

    def __str__(self):
        return self.cod


class User(AbstractUser):
    mobile = models.CharField(max_length=15, blank=True)
    login_list = ArrayField(models.CharField(blank=True, max_length=200, null=True), null=True)
    store = models.ForeignKey(Store, related_name='store', on_delete=models.CASCADE, null=True, blank=True)
    car = models.ForeignKey(Car, related_name='mobile', on_delete=models.CASCADE, null=True, blank=True)
    security_code = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.username


class Cookies(models.Model):
    cod = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
    cast = models.CharField(choices=Choices.cast, blank=True, null=True, max_length=15)
    store = models.ForeignKey(Store, related_name="cookie_store", on_delete=models.CASCADE, null=True, blank=True)
    car = models.ForeignKey(Car, related_name="cookie_car", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Request(models.Model):
    lend = models.ForeignKey(Store, related_name="land", on_delete=models.CASCADE)
    destination = models.ForeignKey(Store, related_name="destination", on_delete=models.CASCADE)
    status = models.CharField(choices=Choices.status, default='processing', max_length=15)
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True, blank=True, max_length=500)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='requests', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.destination.cod} {self.status}'


class CookiesToSent(models.Model):
    cod = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    amount = models.IntegerField(default=0)
    cast = models.CharField(choices=Choices.cast, blank=True, null=True, max_length=15)
    request = models.ForeignKey(Request, related_name='to_sent', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Delivery(models.Model):
    amount = models.IntegerField(default=0)
    time_sent = models.DateTimeField(null=True, blank=True)
    time_arrive = models.DateTimeField(null=True, blank=True)
    latitude = models.FloatField(max_length=50, blank=True, default=0)
    longitude = models.FloatField(max_length=50, blank=True, default=0)
    cargo = models.ForeignKey(Request, related_name='cargo', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, related_name='delivery', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.car.cod} {self.cargo.id}'

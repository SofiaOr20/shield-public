import datetime
import random
import string

import pytz
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import *

from api.serializers import *
from firebase_auth.authentication import FirebaseAuthentication


class StoreListView(generics.ListCreateAPIView):
    queryset = Store.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.GET.get('cookies', False) == 'true':
            return StoreCookiesSerializer
        return StoreSerializer


class CookiesListView(generics.ListCreateAPIView):
    serializer_class = CookiesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        store = self.kwargs.get('id', None)
        if store:
            return Cookies.objects.filter(store_id=store)
        return Cookies.objects.filter(store=self.request.user.store).union(
            Cookies.objects.filter(car=self.request.user.car))

    def perform_create(self, serializer):
        if self.request.user.store:
            serializer.save(store=self.request.user.store)
        else:
            serializer.save(car=self.request.user.car)


class CookiesUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CookiesSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cookie = self.kwargs.get('id', None)
        if cookie and self.request.user.store:
            return Cookies.objects.get(id=cookie, store=self.request.user.store)
        else:
            return Cookies.objects.get(id=cookie, car=self.request.user.car)


class RequestListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.GET.get('param') == 'my':
            return Request.objects.filter(user=self.request.user)
        else:
            return Request.objects.filter(destination=self.request.user.store)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RequestSerializer
        return RequestListSerializer

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user, cookies=self.request.data.get('cookies'))


class RequestUpdateView(generics.UpdateAPIView):
    serializer_class = RequestSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        request = Request.objects.get(id=self.kwargs.get('id', None))
        if request.user == self.request.user or request.lend == self.request.user.store:
            return request
        else:
            return []

    def perform_update(self, serializer):
        return serializer.save(cookies=self.request.data.get('cookies'))


class CarListView(generics.ListAPIView):
    serializer_class = CarSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        param = self.request.GET.get('param', None)
        if param == 'all':
            return Car.objects.all()
        elif param == 'store':
            return Car.objects.filter(delivery__cargo__destination=self.request.user.store)
        return Car.objects.filter(id=self.request.user.car.id)


class DeliveryList(generics.ListCreateAPIView):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.GET.get('param') == 'done':
            return Delivery.objects.filter(car=self.request.user.car, time_sent__isnull=False,
                                           time_arrive__isnull=False)
        elif self.request.GET.get('param') == 'progress':
            return Delivery.objects.filter(car=self.request.user.car, time_sent__isnull=False,
                                           time_arrive__isnull=True)
        elif self.request.GET.get('param') == 'new':
            return Delivery.objects.filter(car=self.request.user.car, time_sent__isnull=True,
                                           time_arrive__isnull=True)
        else:
            return Delivery.objects.filter(car=self.request.user.car).last()

    def perform_create(self, serializer):
        return serializer.save(cargo=Request.objects.get(id=self.request.data.get('cargo_id')),
                               car=Car.objects.get(cod=self.request.data.get('cod')))


class DeliveryUpdateView(generics.UpdateAPIView):
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return Delivery.objects.filter(car=self.request.user.car).last()

    def perform_update(self, serializer):
        kind = self.request.GET.get('type', None)
        if kind == 'sent':
            serializer.save(time_sent=datetime.datetime.now())
        elif kind == 'arrive':
            serializer.save(time_arrive=datetime.datetime.now())
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    key = request.headers.get('Secret-Key')
    user = authenticate(request, username=username, password=password)
    if key == settings.BOT_KEY and user is not None:
        token, create = Token.objects.get_or_create(user=user)
        token = token.key if token else create.key
        user.login_list.append(datetime.datetime.now(tz=pytz.UTC).strftime('%Y-%m-%d, %H:%M:%S'))
        user.save()
        return Response({'token': token}, status=HTTP_200_OK)
    elif user is not None:
        user.security_code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        user.save()
        return Response({'cod': user.security_code, 'mobile': user.mobile}, status=HTTP_200_OK)
    else:
        return Response(status=HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login_firebase(request):
    if request.data.get('cod') == User.objects.get(mobile=request.data.get('mobile')).security_code:
        token = FirebaseAuthentication().authenticate(request)
        user = Token.objects.get(key=token).user
        user.login_list.append(datetime.datetime.now(tz=pytz.UTC).strftime('%Y-%m-%d, %H:%M:%S'))
        user.save()
        return Response({'token': token}, status=HTTP_200_OK)
    else:
        return Response(HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def set_car(request):
    cod = request.data.get('cod', None)
    if cod:
        user = User.objects.get(username=request.user.username)
        user.car = Car.objects.get(cod=cod)
        user.save()
        return Response(status=HTTP_200_OK)
    else:
        return Response(HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes((IsAdminUser,))
def create_user(request):
    user = User.objects.create(**request.data)
    user.login_list.append(datetime.datetime.now(tz=pytz.UTC).strftime('%Y-%m-%d, %H:%M:%S'))
    user.save()
    return Response(status=HTTP_200_OK)

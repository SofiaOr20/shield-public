from rest_framework import serializers
from api.models import *


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'cod', 'address')


class CookiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cookies
        fields = ('id', 'cod', 'name', 'amount', 'cast')


class StoreCookiesSerializer(serializers.ModelSerializer):
    cookie_store = CookiesSerializer(many=True)

    class Meta:
        model = Store
        fields = ('id', 'cod', 'address', 'cookie_store')


class CookiesToSentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookiesToSent
        fields = ('id', 'cod', 'name', 'amount', 'cast')


class RequestSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        lend = Store.objects.get(cod=validated_data.pop('lend'))
        destination = User.objects.get(id=validated_data.get('user').id).store
        cookies = validated_data.pop('cookies')
        request = Request.objects.create(lend=lend, destination=destination, **validated_data)

        for i in cookies:
            CookiesToSent.objects.create(request=request, **i)

        return request

    def update(self, instance, validated_data):
        cookies = validated_data.pop('cookies', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for cookie in cookies:
            to_sent = CookiesToSent.objects.filter(request=instance)
            inst = CookiesToSent.objects.filter(request=instance, cod=cookie['cod'])
            if inst:
                inst_object = inst.last()
                for attr, value in cookie.items():
                    inst_object(inst, attr, value)
                inst_object.save()
                to_sent = to_sent.difference(inst)
            else:
                CookiesToSent.objects.create(request=instance, **cookie)
                to_sent = to_sent.difference(inst)
            for i in to_sent:
                i.delete()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        cookies = CookiesToSent.objects.filter(request=instance)
        representation['to_sent'] = CookiesToSentSerializer(cookies, many=True).data

        return representation

    class Meta:
        model = Request
        fields = ('lend', 'status', 'date', 'comment')


class RequestListSerializer(serializers.ModelSerializer):
    lend = StoreSerializer()
    destination = StoreSerializer()
    to_sent = CookiesToSentSerializer(many=True)

    class Meta:
        model = Request
        fields = ('id', 'lend', 'destination', 'status', 'date', 'comment', 'to_sent')


class DeliverySerializer(serializers.ModelSerializer):
    cargo = RequestSerializer(required=False)

    class Meta:
        model = Delivery
        fields = ('amount', 'time_sent', 'time_arrive', 'latitude', 'longitude', 'cargo')


class CarSerializer(serializers.ModelSerializer):
    delivery = serializers.SerializerMethodField('get_last_delivery')

    def get_last_delivery(self, instance):
        return DeliverySerializer(Delivery.objects.filter(car=instance).last()).data

    class Meta:
        model = Car
        fields = ('cod', 'delivery')

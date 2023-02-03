from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework import authentication
from firebase_admin import auth, credentials, initialize_app

from .exceptions import *

cred = credentials.Certificate('env/shield.json')

default_app = initialize_app(cred)
User = get_user_model()


class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.data.get("token", None)
        username = request.data.get('mobile', None)
        if not auth_header:
            raise NoAuthToken("No auth token provided")

        id_token = auth_header.split(" ").pop()

        try:
            decoded_token = auth.verify_id_token(id_token)
        except Exception:
            raise InvalidAuthToken("Invalid auth token")

        if not id_token or not decoded_token:
            return None

        # try:
        #     print(decoded_token.get("uid"))
        # except Exception:
        #     raise FirebaseError()

        if username:
            user, created = User.objects.get_or_create(mobile=username)
            token, key = Token.objects.get_or_create(user=user) if user else Token.objects.get_or_create(user=created)

        return token.key if token else key.key

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

User = get_user_model()


class JWTRemoteAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        resp = requests.post(
            settings.AUTH_SERVICE_TOKEN_URL,
            json={"username": username, "password": password},
        )
        if resp.status_code != 200:
            return None

        token = resp.json().get("access")
        payload = jwt.decode(token, settings.AUTH_PUBLIC_KEY, algorithms=["RS256"])
        user_id = payload["sub"]

        user, _ = User.objects.using("auth_db").get_or_create(
            id=user_id, defaults={"username": username}
        )
        # Set JWT token as a non-database attribute (will not be persisted)
        user.jwt_token = token  # type: ignore
        return user

    def get_user(self, user_id):
        try:
            return User.objects.using("auth_db").get(pk=user_id)
        except User.DoesNotExist:
            return None

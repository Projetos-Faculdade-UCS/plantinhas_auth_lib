import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from jwt.jwks_client import PyJWKClient

User = get_user_model()


class JWTRemoteAuthBackend(BaseBackend):
    def __init__(self):
        self.jwks_client = None
        if hasattr(settings, "AUTH_BASE_URL"):
            jwks_url = f"{settings.AUTH_BASE_URL.rstrip('/')}/.well-known/jwks.json"
            self.jwks_client = PyJWKClient(jwks_url)

    def authenticate(self, request, username=None, password=None):
        resp = requests.post(
            settings.AUTH_SERVICE_TOKEN_URL,
            json={"username": username, "password": password},
        )
        if resp.status_code != 200:
            return None

        token = resp.json().get("access")

        # Use JWKS endpoint if available, otherwise fall back to static public key
        if self.jwks_client:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(token, signing_key.key, algorithms=["RS256"])
        else:
            raise ValueError(
                "JWKS client not initialized. "
                "Please ensure AUTH_BASE_URL is set in your settings."
            )

        user_id = payload["sub"]

        user = User.objects.using("auth_db").get(id=user_id)
        # Set JWT token as a non-database attribute (will not be persisted)
        user.jwt_token = token  # type: ignore
        return user

    def get_user(self, user_id):
        try:
            return User.objects.using("auth_db").get(pk=user_id)
        except User.DoesNotExist:
            return None

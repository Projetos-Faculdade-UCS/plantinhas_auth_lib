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
            try:
                # First try the normal method that requires "kid" in token header
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(token, signing_key.key, algorithms=["RS256"])
            except jwt.exceptions.PyJWKClientError:
                # If the token doesn't have a "kid", try all available keys
                jwks = self.jwks_client.get_jwk_set()
                for signing_key in jwks.keys:
                    try:
                        payload = jwt.decode(
                            token, signing_key.key, algorithms=["RS256"]
                        )
                        break
                    except jwt.exceptions.InvalidTokenError:
                        continue
                else:
                    # If none of the keys worked, authentication fails
                    return None
        else:
            raise ValueError(
                "JWKS client not initialized. "
                "Please ensure AUTH_BASE_URL is set in your settings."
            )

        # Try to get user ID from various possible JWT claims
        user_id = None
        # First, try to get from configured claim name, defaulting to "sub"
        user_id_claim = getattr(settings, "JWT_USER_ID_CLAIM", "sub")

        if user_id_claim in payload:
            user_id = payload[user_id_claim]
        else:
            # Try common alternative claim names
            for claim in ["id", "user_id", "userId", "userid", "user", "uuid"]:
                if claim in payload:
                    user_id = payload[claim]
                    break

        if not user_id:
            # Print payload for debugging
            print(
                f"JWT payload missing user ID claim. Available claims: {list(payload.keys())}"
            )
            return None

        # Get user from database
        try:
            user = User.objects.using("auth_db").get(id=user_id)
        except User.DoesNotExist:
            return None
        # Set JWT token as a non-database attribute (will not be persisted)
        user.jwt_token = token  # type: ignore
        return user

    def get_user(self, user_id):
        try:
            return User.objects.using("auth_db").get(pk=user_id)
        except User.DoesNotExist:
            return None

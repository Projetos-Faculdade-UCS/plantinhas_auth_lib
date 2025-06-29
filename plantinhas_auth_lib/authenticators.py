from typing import Any
from typing import Optional
from typing import Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

import jwt
from jwt.jwks_client import PyJWKClient

User = get_user_model()


class PlantinhasAuthenticator(BaseAuthentication):
    """
    Custom authenticator for Plantinhas API using JWT token authentication.
    This class uses the same JWT validation logic as the JWTRemoteAuthBackend.
    """

    keyword = "Bearer"

    def __init__(self):
        super().__init__()
        self.jwks_client: Optional[PyJWKClient] = None
        if hasattr(settings, "AUTH_BASE_URL"):
            jwks_url = f"{settings.AUTH_BASE_URL.rstrip('/')}/.well-known/jwks.json"
            self.jwks_client = PyJWKClient(jwks_url)

    def authenticate(self, request: HttpRequest) -> Optional[Tuple[Any, str]]:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith(f"{self.keyword} "):
            return None

        token = auth_header[len(f"{self.keyword} ") :]

        if not token:
            return None

        try:
            # Use JWKS endpoint if available, otherwise raise error
            if not self.jwks_client:
                raise AuthenticationFailed(
                    "JWKS client not initialized. "
                    "Please ensure AUTH_BASE_URL is set in your settings."
                )

            try:
                # First try the normal method that requires "kid" in token header
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                payload = jwt.decode(token, signing_key.key, algorithms=["RS256"])
            except jwt.exceptions.PyJWKClientError:
                # If the token doesn't have a "kid", try all available keys
                jwks = self.jwks_client.get_jwk_set()
                payload = None
                for signing_key in jwks.keys:  # type: ignore
                    try:
                        payload = jwt.decode(
                            token,
                            signing_key.key,  # type: ignore
                            algorithms=["RS256"],  # type: ignore
                        )
                        break
                    except jwt.exceptions.InvalidTokenError:
                        continue

                if payload is None:
                    # If none of the keys worked, authentication fails
                    raise AuthenticationFailed("Invalid token")

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
                raise AuthenticationFailed(
                    f"JWT payload missing user ID claim. "
                    f"Available claims: {list(payload.keys())}"
                )

            # Get user from database
            try:
                user = User.objects.using("auth_db").get(id=user_id)
            except User.DoesNotExist:
                raise AuthenticationFailed("User not found")

            # Set JWT token as a non-database attribute
            setattr(user, "jwt_token", token)
            return (user, token)

        except jwt.exceptions.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except Exception as e:
            raise AuthenticationFailed(f"Authentication error: {str(e)}")

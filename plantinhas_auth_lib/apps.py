from django.apps import AppConfig
from django.conf import settings
from environ import Env


class PlantinhasAuthLibConfig(AppConfig):
    name = "plantinhas_auth_lib"
    verbose_name = "Auth Library"

    def ready(self):
        env = Env()
        # ensure our auth_db router is installed
        routers = list(getattr(settings, "DATABASE_ROUTERS", []))
        routers.insert(0, "plantinhas_auth_lib.db_router.AuthRouter")
        settings.DATABASE_ROUTERS = routers

        # ensure our JWT backend is installed
        backends = list(getattr(settings, "AUTHENTICATION_BACKENDS", []))
        backends.insert(0, "plantinhas_auth_lib.backends.JWTRemoteAuthBackend")
        settings.AUTHENTICATION_BACKENDS = backends

        databases = getattr(settings, "DATABASES", {})

        databases["auth_db"] = env.db("AUTH_DB_URL")

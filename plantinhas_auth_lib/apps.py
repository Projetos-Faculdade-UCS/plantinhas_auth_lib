import os

import dj_database_url
from django.apps import AppConfig
from django.conf import settings


class PlantinhasAuthLibConfig(AppConfig):
    name = "plantinhas_auth_lib"
    verbose_name = "Auth Library"

    def ready(self):
        # ensure our auth_db router is installed
        routers = list(getattr(settings, "DATABASE_ROUTERS", []))
        routers.insert(0, "plantinhas_auth_lib.db_router.AuthRouter")
        settings.DATABASE_ROUTERS = routers

        # ensure our JWT backend is installed
        backends = list(getattr(settings, "AUTHENTICATION_BACKENDS", []))
        backends.insert(0, "plantinhas_auth_lib.backends.JWTRemoteAuthBackend")
        settings.AUTHENTICATION_BACKENDS = backends

        databases = getattr(settings, "DATABASES", {})

        # Use AUTH_DB_URL if available
        auth_db_url = getattr(settings, "AUTH_DB_URL", os.environ.get("AUTH_DB_URL"))

        if auth_db_url:
            # Use dj_database_url to parse the database URL
            db_config = dj_database_url.parse(auth_db_url)

            # Add all required database configuration settings
            # Ensure ATOMIC_REQUESTS is set to prevent KeyError
            db_config.setdefault("ATOMIC_REQUESTS", False)

            # Ensure OPTIONS key exists to prevent KeyError in PostgreSQL backend
            db_config.setdefault("OPTIONS", {})

            # Set TIME_ZONE to prevent KeyError in Django's check_settings
            # Using 'UTC' to provide a valid timezone for ZoneInfo
            db_config.setdefault("TIME_ZONE", "UTC")

            # Add other common database settings that might be checked
            db_config.setdefault("CONN_MAX_AGE", 0)
            db_config.setdefault("CONN_HEALTH_CHECKS", False)
            db_config.setdefault("AUTOCOMMIT", True)

            databases["auth_db"] = db_config
        else:
            raise ValueError(
                "AUTH_DB_URL is not set. "
                "Please set it in your settings or as an environment variable."
            )

        # Update Django's settings
        settings.DATABASES = databases

# Plantinhas Auth Library

A Django authentication library for Plantinhas projects that provides centralized authentication services using JWT tokens and database routing.

## Overview

Plantinhas Auth Library enables Django applications to authenticate users against a remote authentication service using JWT tokens. It routes all authentication-related models to a dedicated authentication database, allowing multiple Django applications to share the same authentication backend while maintaining their own application-specific databases.

## Features

- JWT-based remote authentication backend
- Automatic database routing for authentication models
- Centralized user management across multiple Django applications
- Seamless integration with Django's authentication system

## Requirements

- Python 3.13.2 or higher
- Django 5.2.1 or higher
- A separate authentication database

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/Projetos-Faculdade-UCS/plantinhas_auth_lib.git
```

Or add to your requirements.txt:

```
git+https://github.com/Projetos-Faculdade-UCS/plantinhas_auth_lib.git
```

For a specific version, branch, or commit:

```
# For a specific tag/version
git+https://github.com/Projetos-Faculdade-UCS/plantinhas_auth_lib.git@v0.1.0

# For a specific branch
git+https://github.com/Projetos-Faculdade-UCS/plantinhas_auth_lib.git@main

# For a specific commit
git+https://github.com/Projetos-Faculdade-UCS/plantinhas_auth_lib.git@3a2b1c0
```

## Configuration

### 1. Add to INSTALLED_APPS

Add the app to your Django project's `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'plantinhas_auth_lib',
    
    # Your apps
    # ...
]
```

### 2. Required Settings

Add these settings to your Django project's settings.py:

```python
# Authentication Database URL (required)
AUTH_DB_URL = "postgresql://user:password@localhost:5432/auth_db"
# or set it as an environment variable:
# os.environ["AUTH_DB_URL"] = "postgresql://user:password@localhost:5432/auth_db"

# Authentication Service URL (required)
AUTH_SERVICE_TOKEN_URL = "https://auth.example.com/api/token/"

# Public key for verifying JWT tokens (required)
AUTH_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
YOUR_PUBLIC_KEY_HERE
-----END PUBLIC KEY-----"""
```

### 3. Database Configuration

The library automatically configures the database routing. Your `DATABASES` setting should include at least the default database:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_app_db',
        # ...other database settings
    },
    # Don't manually add 'auth_db' here - the library will do it automatically
}
```

## How It Works

When a user tries to authenticate, the `JWTRemoteAuthBackend` sends the credentials to the specified `AUTH_SERVICE_TOKEN_URL`. If authentication is successful, it:

1. Receives a JWT token from the authentication service
2. Verifies the token using the provided public key
3. Extracts the user ID from the token
4. Creates or retrieves the user from the auth database
5. Attaches the JWT token to the user object for future authenticated requests

All authentication-related models (User, Group, Permission, etc.) are automatically routed to the auth database via the `AuthRouter`.

## Usage Example

Here's a simple view that uses the authentication:

```python
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def protected_view(request):
    # Access the JWT token (useful for making authenticated requests to other services)
    jwt_token = getattr(request.user, 'jwt_token', None)
    
    return JsonResponse({
        'username': request.user.username,
        'authenticated': True
    })
```

## Development

Clone the repository:

```bash
git clone https://github.com/yourusername/plantinhas-auth-lib.git
cd plantinhas-auth-lib
```

Set up a virtual environment and install development dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## Troubleshooting

### Common Issues

1. **DatabaseError: auth_db database is not defined**
   - Make sure `AUTH_DB_URL` is properly set in your settings or as an environment variable

2. **JWT Verification Failed**
   - Verify that `AUTH_PUBLIC_KEY` is correctly set and matches the private key used by the authentication service

3. **ConnectionError: Could not connect to auth service**
   - Check that `AUTH_SERVICE_TOKEN_URL` is correct and the authentication service is running

## License

MIT
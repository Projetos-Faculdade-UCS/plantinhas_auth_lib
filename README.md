# Plantinhas Auth Library

A Django authentication library for Plantinhas projects.

## Features

- Custom authentication backends for Django
- JWT authentication integration
- Request-based authentication helpers
- Database routing for auth models

## Installation

```bash
pip install plantinhas-auth-lib
```

Or add to your requirements.txt:

```
plantinhas-auth-lib==0.1.0
```

## Usage

Add the app to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    # ...
    'plantinhas_auth_lib',
    # ...
]
```

Configure authentication backends:

```python
AUTHENTICATION_BACKENDS = [
    'plantinhas_auth_lib.backends.YourCustomBackend',
    'django.contrib.auth.backends.ModelBackend',
]
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

## License

MIT
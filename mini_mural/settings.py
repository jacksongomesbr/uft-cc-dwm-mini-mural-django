"""Configuração do Django para o Mini Mural.

Os valores que mudam de uma máquina para outra (senha do banco, SECRET_KEY,
DEBUG, endereços aceitos) ficam em config.py, na raiz do projeto, fora do Git.
"""
from pathlib import Path

PASTA_DO_PROJETO = Path(__file__).resolve().parent.parent

try:
    import config
except ModuleNotFoundError:
    raise SystemExit(
        'Arquivo config.py não encontrado.\n'
        'Copie config.exemplo.py para config.py e ajuste os valores.'
    ) from None

SECRET_KEY = config.SECRET_KEY
DEBUG = config.DEBUG
ALLOWED_HOSTS = config.ENDERECOS_ACEITOS

# Só o necessário. Sem admin, auth, sessions nem messages: o mural não tem
# login, e esses apps exigiriam tabelas criadas por migrations.
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'mural',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mini_mural.urls'
WSGI_APPLICATION = 'mini_mural.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        # Procura templates na pasta templates/ de cada app.
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': []},
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': config.BANCO['host'],
        'PORT': config.BANCO['porta'],
        'NAME': config.BANCO['nome'],
        'USER': config.BANCO['usuario'],
        'PASSWORD': config.BANCO['senha'],
    }
}

LANGUAGE_CODE = 'pt-br'
USE_I18N = True

# O banco guarda o instante em UTC (timestamptz). O Django converte para
# TIME_ZONE na hora de mostrar.
TIME_ZONE = config.FUSO_HORARIO
USE_TZ = True

# Endereço dos arquivos estáticos e pasta para onde o collectstatic os copia.
# Em produção, o servidor web entrega essa pasta direto, sem passar pelo Django.
STATIC_URL = 'static/'
STATIC_ROOT = PASTA_DO_PROJETO / 'staticfiles'

# Exceções não tratadas vão para a saída de erro, que o Gunicorn e o
# Apache gravam no log. Sem isto, com DEBUG desligado, o Django só tentaria
# mandar o erro por e-mail.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'django': {'handlers': ['console'], 'level': 'ERROR'}},
}

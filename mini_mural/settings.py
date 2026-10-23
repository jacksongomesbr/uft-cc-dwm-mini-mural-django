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

# Só o necessário. auth guarda usuários e senhas, sessions guarda quem está
# logado, e contenttypes é exigido pelo auth. As tabelas desses três apps
# vêm das migrations do próprio Django (python manage.py migrate); a tabela
# do mural continua vindo de sql/schema.sql. Sem admin nem messages.
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'mural',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Lê o cookie da sessão e carrega request.session.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # A partir da sessão, preenche request.user.
    'django.contrib.auth.middleware.AuthenticationMiddleware',
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
        # request e auth colocam request e user em todo template, para a
        # navegação saber se há alguém logado.
        'OPTIONS': {'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
        ]},
    },
]

# Para onde o @login_required manda quem não entrou, e para onde o login e o
# logout levam depois. São nomes de mural/urls.py.
LOGIN_URL = 'entrar'
LOGIN_REDIRECT_URL = 'mural'
LOGOUT_REDIRECT_URL = 'entrar'

# Regras de senha que o formulário de cadastro aplica. As mensagens saem em
# português por causa do LANGUAGE_CODE.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
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

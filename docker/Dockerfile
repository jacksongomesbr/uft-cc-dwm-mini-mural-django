# Imagem da aplicação: Python com Django e Gunicorn.
FROM python:3.13-slim

# Sem arquivos .pyc e com a saída do Python sem buffer, para os logs
# aparecerem na hora em "docker compose logs".
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# As dependências vêm antes do código: enquanto o requirements.txt não muda,
# o Docker reaproveita esta camada e o build fica rápido.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Só o que a aplicação usa em tempo de execução. O .dockerignore deixa de fora
# o config.py local, o .venv, a documentação e o Git.
COPY manage.py .
COPY mini_mural mini_mural
COPY mural mural
COPY sql sql
COPY docker/config.py config.py

# O Gunicorn roda com um usuário sem privilégios, e não como root. Ele precisa
# de pasta pessoal, onde o Gunicorn cria seu socket de controle. A pasta
# staticfiles/ nasce com esse dono; o volume montado ali herda o dono na
# primeira vez, e o collectstatic consegue gravar.
RUN useradd --create-home mural \
    && mkdir staticfiles \
    && chown mural staticfiles
USER mural

# A cada partida, em ordem:
# 1. migrate cria ou atualiza as tabelas do auth e das sessões;
# 2. carregar_esquema cria a tabela recados e os exemplos, só na primeira vez,
#    porque ela depende de auth_user;
# 3. collectstatic copia os estáticos para o volume que o nginx lê;
# 4. o Gunicorn liga.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py carregar_esquema --se-ausente --exemplos && python manage.py collectstatic --noinput && gunicorn mini_mural.wsgi --bind 0.0.0.0:8000 --workers 3"]

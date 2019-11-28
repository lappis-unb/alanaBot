FROM python:3.7-slim

WORKDIR /celery

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ADD ./docker/celery.requirements.txt /celery/celery.requirements.txt

RUN pip install -r celery.requirements.txt

ADD ./example-palavras-chaves.json /celery/palavras-chaves.json
ADD ./client_secret.json /celery/client_secret.json

# Adiciona todos os scripts
ADD /celery/scripts .


RUN python -c "import nltk; nltk.download('stopwords');"

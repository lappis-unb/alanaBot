FROM python:3.7-slim

WORKDIR /cronjob

RUN apt-get update --fix-missing && apt-get -y install cron

ADD ./docker/cronjob.requirements.txt /cronjob/cronjob.requirements.txt

RUN pip install -r cronjob.requirements.txt

RUN apt-get update && apt-get install --reinstall -y locales tzdata

RUN sed -i 's/# pt_BR.UTF-8 UTF-8/pt_BR.UTF-8 UTF-8/' /etc/locale.gen

RUN locale-gen pt_BR.UTF-8

ENV LANG pt_BR.UTF-8
ENV LANGUAGE pt_BR
ENV LC_ALL pt_BR.UTF-8

RUN dpkg-reconfigure --frontend noninteractive locales

ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN dpkg-reconfigure -f noninteractive tzdata


ADD ./example-palavras-chaves.json /cronjob/palavras-chaves.json
ADD ./client_secret.json /cronjob/client_secret.json

# ADD ./.env /cronjob/.env

# Adiciona todos os scripts
ADD /cronjob/scripts .

# Habilita todos os scripts
RUN chmod +x entrypoint_cron.sh
    # preload_data.sh

RUN python env_loader.py

ADD /cronjob/crontab /etc/cron.d/update-projetos-cron

RUN chmod 0644 /etc/cron.d/update-projetos-cron
RUN crontab /etc/cron.d/update-projetos-cron

RUN python -c "import nltk; nltk.download('stopwords');"

CMD ["./entrypoint_cron.sh"]
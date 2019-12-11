FROM botrequirements

ADD ./bot/actions/ /bot/actions/
ADD ./bot/Makefile /bot/Makefile

WORKDIR /bot

ADD ./client_secret.json /bot/client_secret.json

EXPOSE 5055
HEALTHCHECK --interval=300s --timeout=60s --retries=5 \
  CMD curl -f http://0.0.0.0:5055/health || exit 1

CMD make run-actions

# alanaBot
<!-- badges -->
<a href="https://www.gnu.org/licenses/gpl-3.0.pt-br.html"><img src="https://img.shields.io/badge/licence-GPL3-green.svg"/></a>



## Tutorial para configurar todo o projeto

Para ter seu chatbot Rasa no ar e funcionando rápidamente no `shell` execute o seguinte comando:

```sh
sudo make first-run
```

Este comando irá construir o seu chatbot (containers necessários) e abrir a conversação em um `livechat`
no canto inferior direito da sua tela. Este `mensageiro` é o **WebChat**.

Tudo está dockerizado então você não terá problemas de instalação do ambiente.

## Sobre  o bot

 O bot tem como objetivo o envio de notificações sobre Projetos de Lei. Esse objetivo é concretizado por meio do monitoramento das APIs da [Cãmara dos deputados](https://dadosabertos.camara.leg.br/swagger/api.html) e do [Senado](https://www12.senado.leg.br/dados-abertos), por meio da execução de atividades regulares utilizando o [Celery](https://docs.celeryproject.org/en/latest/getting-started/introduction.html). Também foram utilizadas planilhas e formulários do Google junto com a [API do Google Sheets](https://developers.google.com/sheets/api) para a escolha do usuário sobre os temas que as notificações devem abordar, além da elaboração de relatórios contendo os Projetos de Lei em Planilhas do Google.


### Dependências do Relatório nas planilhas do Google 

Para a elaboração dos relatórios nas Planilhas do Google é necessário o acesso a [API do Google Sheets](https://developers.google.com/sheets/api), portanto um arquivo de configuração para o acesso a API com o nome `client_secret.json` deve ser adicionado na raíz do projeto. Para a geração desse arquivo de configuração visite esse tutorial de [setup da API do google sheets](/docs/setup_google_sheet.md), que abrange desde a criação de um projeto no Google Console até a geração do arquivo de configuração necessário para o correto funcionamento das atividades relacionadas ao relatório.


### Criação de planilhas do Google

Para a elaboração de relatórios nas planilhas do Google é necessário que existam duas planilhas, uma utilizada como template para o relatório incluindo toda formatação de fontes, estilo, espaçamento da linha de colunas e outros. A segunda planilha conterá o relatório de fato e será atualizada diariamente com os Projetos de Lei do dia anterior. Para uma explicação mais detalhada sobre criação das planilhas visite esse [tutorial para a criação de planilhas](/docs/environment_variables.md).

### Criação de formulários

Além disso os relatórios colhem respostas de dois formulários. Um deles serve para seleção de temas que as notificações devem abordar e outro serve para o cadastro de notificações para um dia específico a partir do usuário, para a criação e linkagem desses formulários com as planilhas do Google visite esse [tutorial para criação de formulários](/docs/google_forms_report.md)


### Geração de imagens genéricas

O script `first-run` contido no Makefile foi configurado para construir as imagens genéricas necessárias para execução deste ambiente.
Caso seu projeto utilize este boilerplate e vá realizar uma integração contínua ou similar, é interessante
criar um repositório para as imagens e substitua os nomes das imagens "lappis/bot", e "lappis/botrequirements" pelas suas respectivas novas imagens, por exemplo "<organização>/bot" em repositório público.


### Telegram

Após realizar o [tutorial](/docs/setup_telegram.md) de exportação de todas variávies de ambiente necessárias, é possível realizar a execução do bot no telegram corretamente.

**Antes de seguir adiante. Importante:** As variáveis de ambiente são necessárias para o correto funcionamento do bot, por isso não esqueça de exportá-las.

Edite o arquivo **credentials.yml** e descomente as linhas referentes ao telegram:

```sh
telegram:
 access_token: ${TELEGRAM_TOKEN}
 verify: ${TELEGRAM_BOT_USERNAME}
 webhook_url: ${TELEGRAM_WEBHOOK}
```

Se ainda não tiver treinado seu bot execute antes:

```sh
sudo make train
```

Depois execute o bot no telegram:

```sh
sudo docker-compose up -d bot_telegram
```

### Exportação de variávies de ambientes

Após seguir todos os passos até aqui, é necessário realizar a exportação de todas as variáveis de ambiente do serviço utilizado para agendamento de atividades regulares, após seguir o [tutorial de exportação de variáveis](/docs/environment_variables.md) o arquivo `celery.env` deve ficar parecido com esse.
```sh
TELEGRAM_TOKEN=token
TELEGRAM_DB_URI=mongodb://database-alana:27017/bot
SHEET_ID=your_sheet_id
SHEET_TEMPLATE_ID=your_sheet_template_id
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin
```

### Analytics

Para a visualização dos dados da interação entre o usuário e o chatbot nós utilizamos uma parte da Stack do Elastic, composta pelo ElasticSearch e o Kibana. Com isso, utilizamos um broker para fazer a gerência de mensagens. Então conseguimos adicionar mensagens ao ElasticSearch independente do tipo de mensageiro que estamos utilizando.

### Configuração do RabbitMQ

* Para uma **configuração rápida** execute o seguinte comando:

```sh
sudo make build-analytics
```

O comando acima só precisa ser executado apenas 1 vez e já vai deixar toda a infra de `analytics` pronta para o uso.

Nas próximas vezes que desejar utilizar o `analytics` execute o comando:

```sh
sudo make run-analytics
```

Por fim acesse o **kibana** no `locahost:5601`.


#### Integração com Rasa

Existem duas formas para executar o bot com o *broker*. A primeira delas é via linha de comando.
Para utilizar esta forma é preciso definir Dentro do arquivo `endpoints.yml` as configurações do broker:

```yml
event_broker:
  url: rabbitmq
  username: admin
  password: admin
  queue: bot_messages
```

Ao final é necessário buildar novamente o container do bot.

```
sudo docker-compose up --build -d bot_telegram
```

### Configuração ElasticSearch

O ElasticSearch é o serviço responsável por armazenar os dados provenientes da interação entre o usuário e o chatbot.

As mensagens são inseridas no índice do ElasticSearch utilizando o *broker* RabbitMQ.

Para subir o ambiente do ElasticSearch rode os seguintes comandos:

```
sudo docker-compose up -d elasticsearch
sudo docker-compose run --rm -v $PWD/analytics:/analytics bot python /analytics/setup_elastic.py
```

Lembre-se de setar as seguintes variaveis de ambiente no `docker-compose`.

```
ENVIRONMENT_NAME=localhost
BOT_VERSION=last-commit-hash
```

#### Setup Kibana (Visualização)

Para a análise dos dados das conversas com o usuário, utilize o kibana, e veja como os usuários estão interagindo com o bot, os principais assuntos, média de usuários e outras informações da análise de dados.

O Kibana nos auxilia com uma interface para criação de visualização para os dados armazenados nos índices do ElasticSearch.

```sh
sudo docker-compose up -d kibana
```

**Atenção:** Caso queira configurar permissões diferentes de usuários (Login) no ElasticSearch/Kibana, siga esse tutorial ([link](https://github.com/lappis-unb/rasa-ptbr-boilerplate/tree/master/docs/setup_user_elasticsearch.md)).

#### Importação de dashboards

Caso queira subir com os dashboards que criamos para fazer o monitoramento de bots:

```
sudo docker-compose run --rm kibana python3.6 import_dashboards.py
```

Após rodar o comando anterior os dashboards importados estarão presentes no menu management/kibana/Saved Objects.

Você pode acessar o kibana no `locahost:5601`

## Notebooks - Análise de dados

### Setup

Levante o container `notebooks`

```sh
sudo make run-notebooks
```

Acesse o notebook em `localhost:8888`

# Como conseguir ajuda

Parte da documentação técnica do framework da Tais está disponível na
[wiki do repositório](https://github.com/lappis-unb/tais/wiki). Caso não encontre sua resposta, abra uma issue
com a tag `duvida` que tentaremos responder o mais rápido possível.


# Licença

Todo o bot é desenvolvido sob a licença
[GPL3](https://github.com/lappis-unb/rasa-ptbr-boilerplate/blob/master/LICENSE)
### Configurando dependências para planilhas do google

Para a leitura e escrita de conteúdos relacionados aos Projetos de Lei 
é utilizada a API do Google Sheets, disponibilizada pelo próprio Google.
Portanto é necessário ter um arquivo de configuração com sua chave de API
na raíz do projeto chamado "client_secret.json".

## Criando projeto no Google Console
Para geração de tal arquivo é necessário ter uma conta no 
[console developers do google](http://console.developers.google.com/).
Com a conta criada, acesse o [console](http://console.developers.google.com/) e clique
na aba de projetos no canto superior esquerdo da tela, conforme mostra a imagem a seguir.</br>
![Menu google](/docs/imgs/menu_gconsole.png)

Após clicar nessa opção um novo menu será aberto com a opção
de criar um novo projeto, clique na opção `Novo projeto` como demonstrado abaixo.</br>
![Menu criação projeto](/docs/imgs/menu_projeto_gconsole.png)

Escolha o nome do projeto de acordo com sua preferência e clique em `criar`, assim seu projeto
estará criado.</br>

## Adicionando API do Google sheets ao seu projeto
Com o menu `Painel` selecionado você será capaz de adicionar as APIs do Google ao seu projeto.
Clique em `Ativar APIs e serviços` para visualizar a
biblioteca de API's disponibilizadas pelo Google.</br>
![Menu ativação API](/docs/imgs/menu_ativacao_api.png)

Pesquise por `sheets` e a `Google Sheets API` será exibida, com isso realiza a seleção dela
e na nova tela clique em `Ativar`. Como exibido nas imagens a seguir.</br>
![Pesquisa Sheets API](/docs/imgs/pesquisa_sheets_api.png)

![Aticação Sheets API](/docs/imgs/ativacao_api.png)


## Gerando arquivo com chave de API
Com isso será possível gerar o arquivo com sua chave de API. Selecione o menu `Credenciais` 
e na tela exibida a seguir clique em `Criar credenciais`. Dentre as opções disponíveis
selecione `Chave da conta de serviço` e realize a criação de sua chave de API selecionando 
`JSON` como tipo de chave a ser gerada.
![Credenciais Sheets API](/docs/imgs/criacao_credenciais.png)

Após isso mova o arquivo baixado para a raíz do projeto com o nome `client_secret.json`,
com isso as funcionalidades que utilizam a API do Google Sheets estarão prontas para serem
utilizadass.

Para mais detalhes sobre as chaves que podem ser geradas e a API do Google Sheets acesse 
esse link da [documentação da API do google sheets](https://developers.google.com/sheets/api/guides/concepts)
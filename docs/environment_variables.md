# Ajustando os arquivos de configuração

Esse tutorial tem o objetivo de mostrar as configurações dos arquivos relativos ao Celery
que é um serviço utilizado para a realização de tarefas agendadas sobre os Projetos de Lei, além
das constantes utilizadas para a realização da população do banco de dados e elaboração do 
relatório via planilhas Google.
Antes de seguir adiante tenha certeza que os arquivos de configuração do telegram e da API do google sheets explicados nos tutoriais 
de dependências do [telegram](/docs/Setup/setup_telegram.md), da 
[API do google sheets](/docs/setup_google_sheet.md) e também do [RabbitMQ](README.md), já estão corretamente configurados.


### Utilização de planilhas do Google para relatório

Atualmente são utilizadas duas planilhas para a construção do relatório sobre os Projetos de Lei.
Uma dessas é utilizada somente para definição da formatação do relatório servindo como um `template` 
para o relatório, essa planilha será consultada e todas as cores de fundo, fontes e seus estilos serão
usados como base para a criação do relatório em uma segunda planilha que pode ser criada de maneira simples via Google Drive.

### Criação de planilha via Google Drive

Para criar uma nova planilha no Google Drive, basta acessá-lo via esse [link](drive.google.com) clicar com o botão direito e após selecionar as opções `Planilhas Google` e `Planilha em branco`, Conforme a imagem a seguir.</br>
![Criação de planilha](/docs/imgs/environment_variables/criacao_planilha.png)

### Adicionando permissões para a planilha

Após a criação dessa planilha é necessário adicionar permissão as pessoas que possuem o link para edição e visualização, já que essa permissão será necessária a leitura da planilhade modelo para a criação do relatório.
Para isso clique em compartilhar no canto superior direito da tela.</br>
![Botão compartilhar](/docs/imgs/environment_variables/botao_compartilhar_planilha.png)</br>
Com isso um menu será aberto e deve-se ###clicar em avançado.</br>
![Menu compartilhamento](/docs/imgs/environment_variables/menu_compartilhamento_planilha.png)</br>
Clique em alterar, para realizar as modificações necessárias nas permissões da planilha</br>
![Menu compartilhamento avançado](/docs/imgs/environment_variables/menu_compartilhamento_avancado_planilha.png)</br>
Com o menu das permissões disponíveis, selecione a opção de `qualquer pessoa com o link` e após clique em salvar.</br>
![Alteração de permissão](/docs/imgs/environment_variables/permissoes_planilha.png)</br>
O mesmo processo deve ser realizado oara a planilha em que o relatório será escrito de fato, com base nas formatações da planilha de modelo para o bot.

### Descrição das colunas utilizadas na planilha

Atualmente os scripts funcionam para um número pré-definido de colunas, a descrição delas está a seguir:

| Nome da coluna  | Descrição |
|-----------------|-------------------------------------------------------------------------------------------------------|
| Proposição      | Texto contendo ano e número da proposição com  link para acesso do Projeto de lei |
| Tramitação      | Texto com tramitação do Projeto de Lei |
| Apreciação      | Texto com a apreciação do Projeto de Lei |
| Situação        | Texto como a atual situação do Projeto de Lei |
| Ementa          | Texto como a ementa do Projeto de Lei |
| Autor           | Texto contendo nome do autor do Projeto de Lei e  link para acesso da sua página no site Câmara dos deputados |
| Partido Autor   | Texto com a sigla do partido do Autor |
| Estado Autor    | Estado em que o Autor foi eleito |
| Relator         | Texto contendo nome do relator do Projeto de Lei e link para acesso da sua página no site Câmara dos deputados |
| Partido Relator | Texto com a sigla do partido do Autor |
| Estado Relator  | Texto com a sigla do partido do Relator |
| Apensados       |  Texto com os Projetos de Lei apensados ao  Projeto de Lei atual                  |

### Recuperando Id da planilha do google

Cada planilha possui o seu `Id`, que pode ser encontrado na própria URL do navegador, basta substituir <id_da_planilha>, pela sequência de caracteres existente em uma planilha. Abaixo está um exemplo da URL que contém o `Id` da planilha.
`https://docs.google.com/spreadsheets/d/<id_da_planilha>/edit`

Esse `Id` será utilizado como uma das variáveis de ambiente para a escrita do relatório e também da leitura da planilha de modelo


### Exportando variáveis de ambiente para tarefas agendadas

Substitua o `TELEGRAM_TOKEN` pelo token lhe enviado pelo @BotFather, conforme explicado no [tutorial de setup do telegram](/docs/Setup/setup_telegram.md) 
`SHEET_ID`s pelo `ID` da planilha do Google que você deseja que os 
relatórios sejam salvos, `SHEET_TEMPLATE_ID` pela planilha do Google que será usada como template 
para a criação do relatório e as variávies de configuração do `RABBITMQ` devem ser as mesmas definidas no serviço do `rabbitmq`. No final o arquivo `celery.env` localizado na pasta env na raíz do projeto, estará desse modo.

```sh
TELEGRAM_TOKEN=token
TELEGRAM_DB_URI=mongodb://database-alana:27017/bot
SHEET_ID=your_sheet_id
SHEET_TEMPLATE_ID=your_sheet_template_id
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin
```

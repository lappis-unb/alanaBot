# Comunicação de formulários do Google com planilhas existentes

### Explicação dos formulários existentes

Antes de seguir adiante tenha certeza que as planilhas e todas as suas dependências estejam corretamente instaladas de acordo com o tutorial  para [setup das planilhas e API do google sheets](/docs/environment_variables.md)

Os formulários do Google são utilizados em duas funcionalidades. Uma delas para o cadastro de Palavras Chaves e a outra para o cadastro de Notificações de Newsletter.

O formulário de cadastro de palavras chaves contém duas perguntas, uma delas é a divisão que a pessoa pertence e a segunda é sobre as palavras chaves que devem ser enviadas para pessoas pertencentes a essa divisão. 

Já o formulário de cadastro de newsletter possui três perguntas. A primeira pergunta é a mensagem que deve ser enviada na notificação, a segunda se refere a qual organização essa notificação deve ser enviada e a última pergunta se refere a data em que essa notificação deve ser enviada.

### Linkagem dos formulários com as planilhas existentes

As respostas desses formulários são guardadas nas planilhas existentes, para essa comunicação basta selecionar a opção disponibilizada pelo próprio formulário de vincular as respostas do formulário à uma planilha.
Para vincular clique na aba respostas e após clique no símbolo da planilha do Google e no menu que será aberto clique em `Selecionar planilha existente` e selecione a planilha criada para execução do relatório, como indicado nas imagens a seguir.
![menu google_forms](/docs/imgs/google_forms/google_forms_respostas.png)</br>
![menu google_forms seleção](/docs/imgs/google_forms/google_forms_selecao.png)</br>

Após isso uma aba com as respostas do formulários será gerada na planilha.
Esse processo deve ser feito para os dois formulários e na mesma planilha. A aba da planilha com as respostas do formulário de palavras chaves deve ser renomeada para `Cadastro de palavras chaves`, já as respostas do formulário de newsletter

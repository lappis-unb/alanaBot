## intent:cumprimentar
- oi
- hi
- olá
- ola
- oii
- oie
- hey
- oiee
- opa
- eai
- eaí
- ola boa tarde
- oi alana
- ola alana
- ola alana, tudo bom
- ola alana, que saudade de vc
- oi alana saudades
- posso falar com voce
- pode me tirar uma duvida
- gostaria de tirar uma duvida
- podemos conversar
- bom dia
- boa tarde
- boa noite

## intent:tudo_bem
- oi alana, como estão as coisas
- oi alana, como estao as coisas
- oi alana, como vai
- oi alana, tudo bem
- oi alana, tá bem
- como estão as coisas
- como estao as coisas
- como vai a vida
- como está
- como esta
- como vai
- tudo bem
- tá boa
- tudo de boa
- td de boa
- td bem
- tá bem

## intent:menu_voltar
- quero voltar para o menu
- preciso voltar ao menu
- quero ir para o menu
- quero voltar
- voltar menu
- #voltarmenu
- /voltarmenu
- volta menu
- #voltamenu
- /voltamenu
- #voltar
- voltar
- menu

## intent:out_of_scope
- Você fala sobre o meio ambiente?
- Qual a origem do mundo?
- Você tem signo?
- Vc gosta de carnaval?
- batatinha quando nasce

## intent:ajuda
- [ajuda](command)
- [#ajuda](command)
- [/ajuda](command)
- voce pode me ajudar
- você pode me ajudar
- preciso de ajuda
- sobre o que você sabe falar
- o que mais você sabe falar
- quais assuntos você fala
- o que você sabe 
- lista de assuntos possiveis
- quais as perguntas vc responde
- quais as perquisar você responde
- quero ajuda
- meajuda
- meajude
- MEAJUD
- MEAJDA
- me ajuda
- me ajude
- ajuda eu
- ajuda
- ajudar
- menu

## intent:despedir
- tchau
- até logo
- namaste
- sayonara
- até mais
- até breve
- falou, valeu
- flw vlw
- até mais
- até a próxima

## regex:sugestao_regex
- ^(#|\/|)sugestao

## intent:sugestao
- [/sugestao](sugestao_regex)
- [#sugestao](sugestao_regex)
- [sugestao](sugestao_regex)
- quero te dizer uma sugestão
- quero te dizer uma sugestao
- quero te falar uma sugestão
- quero te falar uma sugestao
- quero te dar uma sugestão
- quero te dar uma sugestao
- quero seu email
- quero um email
- preciso de email
- você podia falar sobre
- voce podia falar sobre
- você precisa melhorar
- vc precisa melhorar
- #sugestão
- sugestão
- email

## regex:sobrenos_regex
- ^(#|\/|)sobrenos

## intent:sobrenos
- [/sobrenos](sobrenos_regex)
- [#sobrenos](sobrenos_regex)
- [sobrenos](sobrenos_regex)
- que tipo de trabalho vocês desenvolvem
- me fala sobre a ong que você trabalha
- me fala sobre o projeto de vocês
- me fala sobre o projeto de voces
- quero saber mais do projeto
- sobre o trabalho de vocês
- projeto prioridade absoluta
- prioridade absoluta
- iniciativa alana
- que ong é essa
- #sobre nós
- #sobre nos
- #sobrenós
- #sobrenos
- /sobrenos
- sobre nós
- sobre nos
- sobrenos

## regex:novidades_regex
- ^(#|\/|)novidades

## intent:novidades
- [novidades](novidades_regex)
- [#novidades](novidades_regex)
- [/novidades](novidades_regex)
- quero ler as últimas novidades
- quero ler as ultimas novidades
- quero ler as últimas tramitações
- quero ler as ultimas tramitacoes
- quero receber as ultimas tramitacoes
- ultimas tramitacoes
- últimas tramitações
- tramitações
- tramitacoes

<!-- actions -->
## regex:cadastro
- ^(#|\/|)cadastrar

## intent:action_cadastro
- [/cadastrar](cadastro)
- [#cadastrar](cadastro)
- [cadastrar](cadastro)
- quero receber notificações de pls
- quero me cadastrar, por favor
- quero receber notificações
- me manda notificações de pls
- me envia as atualizações das leis
- me envia as atualizacoes
- me envia as atualizações
- me envia as notificações
- me envia as notificacoes
- me manda as notificações
- me manda as notificacoes
- me manda notificações
- me manda notificacoes
- me cadastra, por favor
- quero me cadastrar
- quero me inscrever
- notificações
- notificacoes
- me cadastra
- me inscreve
- atualizações
- atualizacoes

## regex:descadastro
- ^(#|\/|)descadastrar

## intent:action_descadastro
- [descadastrar](descadastro)
- [#descadastrar](descadastro)
- [/descadastrar](descadastro)
- para de me mandar notificações
- para de me mandar notificações de pls
- não quero receber notificações de 
- quero me descadastrar, por favor
- não quero receber notificações
- me descadastra, por favor
- não quero mais receber notificações
- nao quero mais receber notificacoes
- não me envia mais notificações
- não me envia mais notificacoes
- não quero mais receber
- nao quero mais receber
- quero me descadastrar
- me descadastra
- descadastrar

## intent:action_start
- [start](command)
- [/start](command)
- oi
- hi
- olá
- ola
- oii
- oie
- hey
- oiee
- opa
- eai
- eaí
- ola boa tarde
- oi alana
- ola alana
- ola alana, tudo bom
- ola alana, que saudade de vc
- oi alana saudades
- posso falar com voce
- pode me tirar uma duvida
- gostaria de tirar uma duvida
- podemos conversar
- bom dia
- boa tarde
- boa noite

## intent:ultimas
- #ultimas 2
- #ultimas 6

## regex:ong_regex
- ^(#|\/|)ong \w+

## intent:ong
- [/ong](ong_regex) teste
- [#ong](ong_regex) alana
- [ong](ong_regex) novaong

## regex:palavrachave_regex
- ^(#|\/|)palavrachave

## intent:palavrachave
- [/palavrachave](palavrachave_regex)
- [#palavrachave](palavrachave_regex)
- [palavrachave](palavrachave_regex) 
- quero cadastrar palavras chaves
- cadastro de palavras chaves
- palavras chaves
- palavra chave por favor
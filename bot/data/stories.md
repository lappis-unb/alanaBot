
<!-- actions -->
## action_cadastro
* cadastrar
  - action_cadastro

## action_descadastro
* descadastrar
  - action_descadastro

## action_start
* start
  - action_start

## action_start+sugestao
* start
  - action_start
* sugestao
  - utter_sugestao
  - action_voltar_menu

## action_ultimas
* ultimas
  - utter_notificacao
  - action_ultimas
  - action_voltar_menu

## novidades+action_ultimas
* novidades
  - utter_novidades
* ultimas
  - utter_notificacao
  - action_ultimas
  - action_voltar_menu

## action_start+action_cadastro
* start
  - action_start
* cadastrar
  - action_cadastro

## action_start+action_descadastro
* start
  - action_start
* descadastrar
  - action_descadastro

## path_ultimas+sugestao
* ultimas
  - utter_notificacao
  - action_ultimas
* sugestao
  - utter_sugestao
  - action_voltar_menu

## path_ultimas+sobrenos
* ultimas
  - utter_notificacao
  - action_ultimas
* sobrenos
  - utter_sobrenos
  - action_voltar_menu

<!-- geral -->

## path_cumprimentar
* cumprimentar
    - utter_cumprimentar

## path_cumprimentar+sobrenos
* cumprimentar
  - utter_cumprimentar
* sobrenos
  - utter_sobrenos
  - action_voltar_menu

## path_cumprimentar+ajuda
* cumprimentar
  - utter_cumprimentar
* ajuda
  - utter_ajuda
  - action_menu

## path_cumprimentar+sugestao
* cumprimentar
  - utter_cumprimentar
* sugestao
  - utter_sugestao
  - action_voltar_menu

## path_cumprimentar+cadastrar
* cumprimentar
  - utter_cumprimentar
* cadastrar
  - action_cadastro

## path_cumprimentar+descadastrar
* cumprimentar
  - utter_cumprimentar
* descadastrar
  - action_descadastro

## fallback
* out_of_scope
    - utter_default

## path_ajuda
* ajuda
  - utter_ajuda
  - action_menu

## path_ajuda+sugestao
* ajuda
  - utter_ajuda
  - action_menu
* sugestao
  - utter_sugestao
  - action_voltar_menu

## path_menu
* menu_voltar
  - action_menu

## path_menu+sobrenos
* menu_voltar
  - action_menu
* sobrenos
  - utter_sobrenos
  - action_voltar_menu

## path_menu+sugestao
* menu_voltar
  - action_menu
* sugestao
  - utter_sugestao
  - action_voltar_menu

## path_despedir
* despedir
  - utter_despedir

## path_tudo_bem
* tudo_bem
  -  utter_tudo_bem

## path_tudo_bem
* tudo_bem
  -  utter_tudo_bem
* sobrenos
  - utter_sobrenos

## path_tudo_bem+sobrenos
* tudo_bem
  -  utter_tudo_bem
* sobrenos
  - utter_sobrenos
  - action_voltar_menu

## path_tudo_bem+ajuda
* tudo_bem
  -  utter_tudo_bem
* ajuda
  - utter_ajuda
  - action_menu

## path_sugestao
* sugestao
  - utter_sugestao
  - action_voltar_menu

## path_sugestao+menu
* sugestao
  - utter_sugestao
  - action_voltar_menu
* menu_voltar
  - action_menu

## path_novidades
* novidades
  - utter_novidades

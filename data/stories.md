## say hello
* saludo
 - action_hello

## say goodbye
* despedida
  - utter_despedida
  - action_restart
  
## estoy bien path
* como_estas
  - utter_estoy_bien
  - utter_como_estas
* estoy_bien
  - utter_me_alegro
  - utter_te_puedo_ayudar

## no estoy bien path
* como_estas
  - utter_estoy_bien
  - utter_como_estas
* no_estoy_bien
  - utter_vaya_hombre
  - utter_te_puedo_ayudar

## no estoy bien path 2
* no_estoy_bien
  - utter_vaya_hombre
  - utter_te_puedo_ayudar  
  
## donde vives
* de_donde_eres
  - utter_donde_vivo
  
## quien te ha creado
* quien_te_ha_creado
  - utter_mis_padres
  
## siguientes charlas
* siguiente_charla
  - action_find_next_talks

## a que hora es la charla
* a_que_hora
  - slot{"speaker":"Rafa Haro"}
  - action_find_talk
  - action_listen

## a que hora es la charla desam
* a_que_hora
  - slot{"speaker":"Rafa Haro"}
  - action_find_talk
  - slot{"found_speakers": "Antonio"}
  - speaker_form
  - form{"name": "speaker_form"}
  - slot{"requested_slot": "confirmed_speaker"}
  
## a que hora es la charla sobre
* a_que_hora_title
  - slot{"talk":"microservicios"}
  - action_find_talk
  - action_listen

## que hay a las
* que_hay_a_las
  - slot{"time":"11:30"}
  - slot{"day":"sabado"}
  - action_find_talks_by_time
  - action_listen
  
## que hay a las sin dia
* que_hay_a_las
  - action_find_talks_by_time{"time":"11:30"}
  - form{"name": "talk_form"}
  - action_find_talks_by_time{"time":"11:30","day":"sabado"}
  
## que hay a las sin hora
* que_hay_a_las
  - action_find_talks_by_time{"day":"domingo"}
  - form{"name": "talk_form"}
  - action_find_talks_by_time{"time":"11:30","day":"domingo"}
  
  
  
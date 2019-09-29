## intent:saludo
- hola
- buenas
- hola, como estas?
- buenos días
- buenas tardes
- buenas noches
- que pasa
- saludos

## intent:despedida
- adios
- nos vemos
- hasta luego
- enga quillo
- bye

## intent:negacion
- no
- nunca
- no creo
- que va
- te estas equivocando

## intent:como_estas
- Cómo estás
- Cómo te encuentras
- Qué pasa
- Qué haces
- Como andamos
- qué te cuentas
- como va la vida

## intent:estoy_bien
- de arte
- de categoria
- bien
- estupendo
- muy bien
- estoy bien
- no estoy mal
- aquí andamos

## intent:no_estoy_bien
- estoy mal
- triste
- mal
- horrible
- regular
- no estoy bien

## intent:de_donde_eres
- de dónde eres?
- de dónde vienes?
- dónde vives?
- de dónde sales?

## intent:quien_te_ha_creado
- quién te ha creado?
- quién te ha programado?
- quién es tu padre?

## intent:a_que_hora
- a qué hora es la charla de [Rafa Haro](speaker)
- cuando es la charla de [Antonio David Perez](speaker)
- a qué hora presenta [María Marcos](speaker)
- cuándo es la charla de [Guillem Duran](speaker)
- cuando habla [Alberto](speaker)
- a que hora es la charla de [antonio](speaker)
- a qué hora es la presentación de [Orange](speaker)
- cuando presenta [Ravenpack](speaker)

## intent:a_que_hora_title
- a qué hora es la charla sobre [microservicios](talk)
- cuántas charlas hay de [Django](talk)
- a qué hora son las charlas sobre [NLP](talk)
- [Python para calentar tu casa](talk)
- a qué hora son las charlas [patrocinadas](talk)
- hay alguna charla de [Big Data](talk)
- [Django](talk)
- [PySOA](talk)
- alguna charla de [Dask](talk)
- cuando es la charla de [Reconocimiento del habla en Python](talk)
- charla [When code is not enough](talk)

## intent:siguiente_charla
- cuál es la siguiente charla?
- siguiente charla
- quien presenta ahora

## intent:que_hay_a_las
- que charlas hay a las [11:30](time)?
- que hay a las [12](time)?
- que charlas hay [hoy](day) a las [17:00](time)
- que hay [mañana](day) a las [14:30](time)
- que charlas hay el [sabado](day) a las [11:00](time)
- charlas el [domingo](day) a la [13:00](time)?
- quién presenta el [sabado](day) a las [17](time)?
- que charlas hay el [sabado](day)
- charlas del [domingo](day)
- [hoy](day)
- [sabado](day)
- el [domingo](day)
- [12:10](time)
- [17](time)
- [1](time)

## intent:donde_es
- dónde es la charla de [Antonio](speaker)
- dónde presenta [Rafa](speaker)

## regex:time
- ([01]?[0-9]|2[0-3])(:[0-5][0-9])?

## lookup:day
- hoy
- mañana
- el sabado
- el domingo
- el sábado
- sábado
- domingo

## lookup:speaker
data/speakers.txt

## lookup:talk
data/talks.txt

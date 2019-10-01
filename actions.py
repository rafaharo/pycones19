# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"
import string
from collections import defaultdict

import yaml
import unidecode
from datetime import datetime, timedelta
from elasticsearch_dsl import connections, Q
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, ReminderScheduled
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from typing import Any, Text, Dict, List, Union, Optional
from stop_words import get_stop_words

from model import Talk

elastic_endpoint = 'localhost'

with open("config.yml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        elastic_endpoint = config.get('endpoints')[0].get('elasticsearch')
    except yaml.YAMLError as exc:
        print(exc)

connections.create_connection(hosts=[elastic_endpoint])

talks_db = {}
stop_words = get_stop_words('es')


def tokenize(text):
    input_normalized = unidecode.unidecode(text.lower()).strip(string.punctuation)
    tokens = input_normalized.split(' ')
    return [token for token in tokens if token not in stop_words]

with open('./data/talks.txt') as fp:
    lines = fp.readlines()
    for line in lines:
        line = line.replace('\n', '')
        talks_db[line] = tokenize(line)


def search_talks_database(tokens):
    candidates = []
    winner = 0
    for talk, tokens_candidates in talks_db.items():
        intersect = list(set(tokens) & set(tokens_candidates))
        intersected = len(intersect)
        if intersected > 0:
            if intersected > winner:
                candidates = [talk]
            elif intersected == winner:
                candidates.append(talk)
    return candidates


class ActionHelloAndScheduleReminder(Action):

    def name(self) -> Text:
        return "action_hello"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_template('utter_saludo', tracker)
        return [ReminderScheduled('action_schedule_reminder', datetime.now() + timedelta(seconds=30),
                                  kill_on_user_message=True)]


class ActionScheduleReminder(Action):

    def name(self) -> Text:
        return "action_schedule_reminder"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_template('utter_reminder', tracker)
        return []


class ActionFindNextTalks(Action):

    def name(self) -> Text:
        return "action_find_next_talks"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        now = datetime.now()
        # now = datetime.strptime("2019-10-06 11:00", '%Y-%m-%d %H:%M')
        search = Talk.search()
        query = search.sort('start').query('range', start={'gt': now})
        if query.count() == 0:
            dispatcher.utter_message("Pues ahora mismo no encuentro ninguna")
        else:
            message = "Las próximas charlas que he encontrado son:\n"
            message += range_query_to_message(query)
            dispatcher.utter_message(message)

        return []


class ActionFindTalksByTime(Action):

    def name(self) -> Text:
        return "action_find_talks_by_time"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        search = Talk.search()
        time_slot = tracker.get_slot('time')
        day_slot = tracker.get_slot('day')

        if time_slot and day_slot:
            if day_slot.lower() == 'hoy' or day_slot.lower() == 'mañana':
                weekday = datetime.today().weekday()
                if day_slot.lower() == 'mañana':
                    weekday += 1
                if weekday == 5:
                    day = 'Sabado'
                elif weekday == '6':
                    day = 'Domingo'
                else:
                    dispatcher.utter_message("Solo tengo registradas charlas el Sábado y Domingo\n")
                    return []
            else:
                day = unidecode.unidecode(day_slot).lower()
                if day != 'sabado' and day != 'domingo':
                    dispatcher.utter_message("Solo tengo registradas charlas el Sábado y Domingo\n")
                    return []

            if ':' in time_slot:
                time_parts = time_slot.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1])
            else:
                hour = int(time_slot)
                minute = 0

            if day == 'sabado':
                date = datetime(year=2019, month=10, day=5, hour=hour, minute=minute)
            else:
                date = datetime(year=2019, month=10, day=6, hour=hour, minute=minute)

            query = search.sort('start').\
                query('term', day=day).\
                query('range', start={'gte': date})
            if query.count() == 0:
                dispatcher.utter_message("No he encontrado ninguna charla el dia {} a las {}\n".format(day, time_slot))
            else:
                message = "He encontrado las siguientes charlas el dia {} a las {}:\n".format(day, time_slot)
                message += range_query_to_message(query)
                dispatcher.utter_message(message)
                return[SlotSet('time', None), SlotSet('day', None)]

        elif time_slot and not day_slot:
            dispatcher.utter_message("¿Qué día, Sábado o Domingo?\n")
        elif day_slot and not time_slot:
            dispatcher.utter_message("¿A qué hora?\n")
        else:
            dispatcher.utter_message("He entendido que buscas una charla, pero no he encontrado día ni hora\n")

        return []


class SpeakerForm(FormAction):

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "talk_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["day", "time"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "day": self.from_entity("day"),
            "time": self.from_entity("time")
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        dispatcher.utter_message("Perfecto! Voy a ver que encuentro\n")
        return []


def range_query_to_message(query):
    first_talk = query[0].execute()
    talks = [first_talk[0]]
    results = query[1:].execute()
    for talk in results:
        if talk.start == first_talk[0].start and talk.day == first_talk[0].day:
            talks.append(talk)
        else:
            break
    titles = [t.title + " - " + '/'.join(t.speakers) + " en " + t.place for t in talks]
    return '\n'.join(titles)


class ActionFindTalk(Action):

    def name(self) -> Text:
        return "action_find_talk"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        search = Talk.search()
        talk_slot = tracker.get_slot('talk')
        if talk_slot:
            query = search.sort('start').query('match', title=talk_slot)
            if query.count() > 0:
                talks = []
                for t in query:
                    talks.append(
                        t.title + " el " + t.day + " a las " + t.start.strftime('%H:%M') + " en " + t.place)
                dispatcher.utter_message("Las charlas que he encontrado son:\n{}".
                                         format('\n'.join(talks)))
            else:
                dispatcher.utter_message("No he encontrado ninguna charla sobre ese tema. ¿Puedes reformular la pregunta?")
            return [SlotSet('talk', None)]

        speaker = tracker.get_slot('speaker')
        if speaker:
            query = search.sort('start').query('match', speakers=speaker)
            if query.count() > 0:
                # TODO Replace this ugly code by an Elastic Aggregation. Make speakers field a keyword as well
                talksBySpeaker = defaultdict(list)
                for t in query:
                    t.speakers.sort()
                    for s in t.speakers:
                        if speaker.lower() in s.lower():
                            talksBySpeaker[s].append(t)
                if len(talksBySpeaker) == 1:
                    talks = []
                    for t in list(talksBySpeaker.values())[0]:
                        talks.append(
                            t.title + " el " + t.day + " a las " + t.start.strftime('%H:%M') + " en " + t.place)
                    dispatcher.utter_message("Las charlas que he encontrado de {} son:\n{}".
                                             format(speaker, '\n'.join(talks)))
                else:
                    found_speakers = talksBySpeaker.keys()
                    message = "¿A qué '{}' te refieres?. He encontrado {}:\n{}".\
                        format(speaker, len(talksBySpeaker), '\n'.join(found_speakers))
                    dispatcher.utter_message(message)
                    return[SlotSet("found_speakers", list(found_speakers))]
            else:
                query = search.sort('start').query('match', title=speaker)
                if query.count() == 0:
                    dispatcher.utter_message("No he encontrado ninguna charla de {}".format(speaker))
                else:
                    talks = []
                    for t in query:
                        talks.append(
                            t.title + " el " + t.day + " a las " + t.start.strftime('%H:%M') + " en " + t.place)
                    dispatcher.utter_message("Las charlas que he encontrado de {} son:\n{}".
                                             format(speaker, '\n'.join(talks)))
                return[SlotSet("speaker", None)]
        else:
            tokens = tokenize(tracker.latest_message.get('text'))
            candidates = search_talks_database(tokens)
            if len(candidates) > 0:
                shoulds = []
                for candidate in candidates:
                    shoulds.append(Q('match_phrase', title=candidate))
                q = Q('bool', should=shoulds)
                query = search.sort('start').query(q)
                if query.count() == 0:
                    dispatcher.utter_message("No he podido encontrar ninguna charla, lo siento".format(speaker))
                else:
                    talks = []
                    for t in query:
                        talks.append(
                            t.title + " el " + t.day + " a las " + t.start.strftime('%H:%M') + " en " + t.place)
                    dispatcher.utter_message("Las posibles charlas relevantes que he encontrado son:\n{}".
                                             format('\n'.join(talks)))
            else:
                dispatcher.utter_message("No he encontrado ninguna charla. ¿Puedes reformular la pregunta?")

        return []


class SpeakerForm(FormAction):

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "speaker_form"

    @staticmethod
    def ordinal_db() -> Dict[Text, int]:
        """Database of supported cuisines"""

        return {
            "el primero": 0,
            "el segundo": 1,
            "el tercero": 2,
            "el cuarto": 3,
            "el quinto": 4,
            "el sexto": 5,
        }

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["confirmed_speaker"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""

        return {
            "confirmed_speaker": self.from_text()
        }

    def validate_confirmed_speaker(
            self,
            value: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> Optional[Text]:
        """Validate cuisine value."""

        found_speakers = tracker.get_slot('found_speakers')
        if not found_speakers:
            self.deactivate()
            return {"confirmed_speaker": None}

        matches = []
        if value.lower() in self.ordinal_db():
            index = self.ordinal_db().get(value.lower())
            if index < len(found_speakers):
                matches.append(found_speakers[index])
        else:
            for speaker in found_speakers:
                if unidecode.unidecode(value).lower() in unidecode.unidecode(speaker).lower():
                    matches.append(speaker)

        if len(matches) == 0:
            dispatcher.utter_message("No me suena {}. Prueba otra vez".format(value))
            return {"confirmed_speaker": None}
        elif len(matches) == 1:
            return {"confirmed_speaker": matches[0]}
        else:
            dispatcher.utter_message("{} pueden ser:\n {}\n. ¿Puedes ser más preciso amigo?".
                                     format(value, '\n'.join(matches)))
            return {"confirmed_speaker": None}

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        speaker = tracker.get_slot('confirmed_speaker')
        search = Talk.search()
        query = search.sort('start').query('match_phrase', speakers=speaker)
        talks = []
        for t in query:
            talks.append(
                t.title + " el " + t.day + " a las " + t.start.strftime('%H:%M') + " en " + t.place)
        dispatcher.utter_message("Las charlas que he encontrado de {} son:\n{}".
                                 format(speaker, '\n'.join(talks)))
        self.deactivate()
        return [SlotSet("confirmed_speaker", None), SlotSet("found_speakers", None), SlotSet('speaker', None)]

import pandas as pd
from elasticsearch_dsl import connections, Index
from model import Talk
from datetime import datetime

if __name__== "__main__":

    # Indexes Reset
    connections.create_connection(hosts=['localhost'])
    talks_index = Index(Talk.Index.name)
    talks_index.delete(ignore=404)
    talks_index.create()

    talks_df = pd.read_csv('./data/talks.txt')
    print("Number of talks in the report: {}".format(len(talks_df)))

    for index, row in talks_df.iterrows():
        next_talk = Talk()
        next_talk.title = row['Title']
        next_talk.speakers = row['Speakers'].split('/')
        next_talk.day = row['Day']
        next_talk.place = row['Place']
        next_talk.type = row['Type']
        next_talk.start = datetime.strptime(row['Start'], '%H:%M')
        if next_talk.day.startswith("s"):
            next_talk.start = next_talk.start.replace(year=2019, month=10, day=5)
        else:
            next_talk.start = next_talk.start.replace(year=2019, month=10, day=6)
        next_talk.end = datetime.strptime(row['End'], '%H:%M')
        if next_talk.day.startswith("s"):
            next_talk.end = next_talk.end.replace(year=2019, month=10, day=5)
        else:
            next_talk.end = next_talk.end.replace(year=2019, month=10, day=6)
        try:
            next_talk.save()
        except Exception as e:
            print (e.message)

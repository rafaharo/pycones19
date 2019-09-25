from elasticsearch_dsl import Document, Integer, Keyword, Text, Date


class Talk(Document):

    title = Text()
    speakers = Text(multi=True)
    day = Keyword()
    type = Keyword()
    place = Keyword()
    start = Date()
    end = Date()

    class Index:
        name = 'talks'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1
        }

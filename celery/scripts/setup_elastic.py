import logging
import os
import argparse

from elasticsearch import Elasticsearch

parser = argparse.ArgumentParser(description="configures elastic")
parser.add_argument(
    "--task", "-t", default="setup", choices=["setup", "delete"]
)
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

es_user = os.getenv("ELASTIC_USER")
if es_user is not None:
    es_pass = os.getenv("ELASTIC_PASS")
    es = Elasticsearch([os.getenv("ELASTICSEARCH_URL", "elasticsearch:9200")],
                       http_auth=(es_user, es_pass))
else:
    es = Elasticsearch([os.getenv("ELASTICSEARCH_URL", "elasticsearch:9200")])
settings = {
    "settings": {
        "analysis": {
            "filter": {
                "brazilian_stop": {
                    "type": "stop",
                    "stopwords":  "_brazilian_"
                },
                "brazilian_keywords": {
                    "type": "keyword_marker",
                    "keywords":   []
                },
                "brazilian_stemmer": {
                    "type":       "stemmer",
                    "language":   "brazilian"
                }
            },
            "analyzer": {
                "rebuilt_brazilian": {
                    "tokenizer":  "standard",
                    "filter": [
                        "lowercase",
                        "brazilian_stop",
                        "brazilian_keywords",
                        "brazilian_stemmer"]
                }
            }
        }
    },
    "mappings": {
        "project": {
            "properties": {
                'ongName': {"type": "keyword"},
                'ementa': {
                    "type": "text",
                    "analyzer": "rebuilt_brazilian",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },
                'tramitacao': {
                    "type": "text",
                    "analyzer": "rebuilt_brazilian",
                    "fields": {
                        "raw": {
                            "type": "keyword"
                        }
                    }
                },
                'situacao': {"type": "keyword"},
                'sigla': {"type": "keyword"},
                'numero': {"type": "keyword"},
                'ano': {"type": "keyword"},
                'data': {"type": "date", "format": "yyyy/MM/dd"},
                'urlPL': {"type": "keyword"},
                'casa': {"type": "keyword"},
                'tags_ementa': {"type": "keyword"},
                'tags_tramitacao': {"type": "keyword"},
                'keywords': {"type": "keyword"},
                'autor': {
                    "properties": {
                        "id": {"type": "keyword"},
                        "urlParlamentar": {"type": "keyword"},
                        "urlApiParlamentar": {"type": "keyword"},
                        'nome': {"type": "keyword"},
                        'sexo': {"type": "keyword"},
                        'estado': {
                            "properties": {
                                "uf": {"type": "keyword"},
                                "coord": {"type": "geo_point"}
                            }
                        },
                        'siglaPartido': {"type": "keyword"}
                    }
                },
                'relator': {
                    "properties": {
                        "id": {"type": "keyword"},
                        "urlParlamentar": {"type": "keyword"},
                        "urlApiParlamentar": {"type": "keyword"},
                        'nome': {"type": "keyword"},
                        'sexo': {"type": "keyword"},
                        'estado': {
                            "properties": {
                                "uf": {"type": "keyword"},
                                "coord": {"type": "geo_point"}
                            }
                        },
                        'siglaPartido': {"type": "keyword"}
                    }
                }
            }
        }
    }
}

param = {"include_type_name": "true"}

index_name = "projects"

if __name__ == "__main__":
    if args.task == "setup":
        try:
            if not es.indices.exists(index_name):
                logger.debug(
                    es.indices.create(
                        index=index_name,
                        ignore=400,
                        params=param,
                        body=settings,
                    )
                )
                logger.info("Created Index")
            else:
                logger.info("Index {} already exists".format(index_name))
        except Exception as ex:
            logger.error(str(ex))

    elif args.task == "delete":
        logger.debug(es.indices.delete(index=index_name, ignore=[400, 404]))
        logger.info("Index deleted")

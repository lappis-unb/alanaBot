from requests import get
import logging
import time
from requests.exceptions import ConnectionError
import json
import constants
try:
    from nltk.corpus import stopwords
except Exception:
    import nltk

    nltk.download("stopwords")
    from nltk.corpus import stopwords


def search_keyword(search_string, keywords_list):
    if any(keyword.lower() in search_string.lower()
            for keyword in keywords_list):
        return True
    else:
        return False


def can_connect(request_str):
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        req_projeto = get(request_str, headers=headers)
    except ConnectionError:
        print("CONNECTION ERROR")
        raise ConnectionError
    else:
        return req_projeto


def get_request(request_str):
    for _ in range(100):
        try:
            req_projeto = can_connect(request_str)
        except ConnectionError:
            print("API is unavailable. Retrying "
                  "in 0.5 seconds")
            logging.warning("API is unavailable. Retrying "
                            "in 0.5 seconds")
            time.sleep(0.5)
            continue
        else:
            print("API is available. Continuing...")
            logging.info("API is available. Continuing...")
            return req_projeto
    logging.critical('Maximum number of attempts connecting to API')
    raise ConnectionError


def fetch_palavras_chaves(self):
    """
    Read the keywords json and returns it as a dict.

    Returns
    -------
    list of dicts:
        [
            {
                "Name": str -> Specify keyword subject,
                "keywords": list of str -> All subject keywords
            }
        ]
    """
    json_palavras_chaves = open(constants.JSON_PALAVRAS_CHAVES,
                                encoding="utf-8")
    palavras_chaves_str = json_palavras_chaves.read()
    dict_palavras_chaves = json.loads(palavras_chaves_str)
    return dict_palavras_chaves


def fetch_palavras(palavras_chaves):
    """
    Read the keywords json and returns it as a list of dicts.

    Args
    -------
    palavras_chaves:
        list of dicts ->
        [
            {
                "Name": str -> Specify keyword subject,
                "keywords": list of str -> All subject keywords
            }
        ]

    Returns
    -------
        list of str -> All keywords from all subjects
    """
    palavras = []
    for i, _ in enumerate(palavras_chaves):
        for palavra_chave in palavras_chaves[i]["keywords"]:
            palavras.append(palavra_chave)
    return palavras


def get_tags_from_string(text):
    tags = []
    for word in (
        text
        .replace(". ", " ")
        .replace(",", " ")
        .replace('"', "")
        .replace("'", "")
        .replace("*", "")
        .replace("(", "")
        .replace(")", "")
        .replace("º", "")
        .replace("-", "")
        .split(" ")
    ):
        if (
            word.lower() not in stopwords.words("portuguese")
            and len(word) > 1
        ):
            tags.append(word)
    return tags


def save_brazilian_states_json():
    req_json = get_request("https://vector.maps.elastic.co/files/"
                           "brazil_states_v1.geo.json?elastic_tile"
                           "_service_tos=agree&my_app_name=kibana&"
                           "my_app_version=7.4.0&license="
                           "643c1faf-80fc-4ab0-"
                           "9323-4d9bd11f4bbc").json()
    with open('brazilian_states.json', 'w') as fp:
        json.dump(req_json, fp)


def save_projeto_to_db(db_data):
    """
    Save data from pl, deputy and reporter to database
    Args
    -------
    db_data:
        dict -> all pl data
    """
    constants.DB.Project.insert_one(db_data)

import json
import requests
import time
import urllib 
from sklearn.feature_extraction.text import TfidfVectorizer

TOKEN = "1098843018:AAGufk-8qK134xlUiuZUny2n8cg6l7IXDdU"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)

with open('keys.txt', encoding = "utf8") as file:
    keys = json.loads(file.read())
with open('movie.txt', encoding = "utf8") as file:
    data = json.loads(file.read().lower())
vectorizer = TfidfVectorizer(min_df=1)

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

def get_json_from_url(url):    
    content = get_url(url)
    js = json.loads(content)
    return js

def get_updates(offset=None):
    url = URL + "getUpdates"
    if offset:
        url += "?offset={}".format(offset)
    js = get_json_from_url(url)
    return js

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

#bot code running inside 

def data_out(updates):
    for update in updates["result"]:
        print(update, end='\n\n')
        try:
            query = update["message"]["text"]
            chat = update["message"]["chat"]["id"]
            sim =[]
            for doc in data:
                tfidf = vectorizer.fit_transform([doc, query])
                similarity = (tfidf * tfidf.T).A[0,1]
                sim.append(similarity)
            maxIndex = 0
            for index in range(sim.__len__()):
                if sim[index] > sim[maxIndex]:
                    maxIndex = index
            response = keys[maxIndex]
            send_message(response, chat)
        except Exception:
            pass

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return (text, chat_id)

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            data_out(updates)
        time.sleep(0.05)


if __name__ == '__main__':
    main()
from flask import Flask
from flask_ask import Ask, statement, question
import requests
import time
import unidecode
import json
import numpy as np

app = Flask(__name__)
ask = Ask(app, '/')

good, titles, texts = [], [], []
@app.route('/')
def homepage():
    return "Hello"

@ask.launch
def start_skill():
    msg = "Hello. Would you like to hear a joke?"
    return question(msg)

def get_joke():
    #return "Newsy news blah blah news news."
    global titles
    global texts
    global good
    if len(good) == 0:
        user_cred = {'user': 'cogworks2017',
                     'passwd': 'beaverworks',
                     'api_type': 'json'}
        sess = requests.Session()
        sess.headers.update({'User-Agent': 'cogworks'})
        sess.post('https://www.reddit.com/api/login', data=user_cred)

        url = 'https://reddit.com/r/jokes/.json?limit=20'
        html = sess.get(url)
        data = json.loads(html.content.decode('utf-8'))
        titles = [unidecode.unidecode(x['data']['title']) for x in data['data']['children']]
        texts = [unidecode.unidecode(x['data']['selftext']) for x in data['data']['children']]
        long = [x['data']['link_flair_css_class'] == 'long' for x in data['data']['children']]
        nsfw = ['NSFW' in x for x in titles]
        for i, t in enumerate(titles):
            if not long[i] and not nsfw[i]:
                good.append(i)
    i = np.random.choice(good)
    del good[good.index(i)]

    return titles[i], texts[i]
@ask.intent("YesIntent")
def share_joke():
    title, joke = get_joke()
    msg = title + "... " + joke
    return statement(msg)

@ask.intent("NoIntent")
def no_intent():
    msg = "Ok, thanks. Have a nice day."
    return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)

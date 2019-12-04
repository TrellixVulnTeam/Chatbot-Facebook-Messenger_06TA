#import to messenger api
import os,sys
from flask import Flask, request
from pymessenger.bot import Bot


#import to chatbot
import numpy as np
from sklearn import tree
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,strip_accents='unicode')

intencaos = []
corpus = []
pedido = []




TOKEN_PAGE= "EAAGfWvt5cFABABPOOZCJT05oIylakwKQo9VtTwrO1d1019scBO2rsYV9VdDhP3A4iMujGmrj3FLYTiVZCZAZAQLGTVT1pScl4pJKxauDfC2HBYilPlu3P9oa7SwvqGPpW8253e1zKMfHZAZCyIb6OqTsQmMWISKHX2h4SLbCbHIfZAznIkgksHf"
bot = Bot(TOKEN_PAGE)
app = Flask(__name__)

@app.route('/',methods=['GET'])
def verify():
    if request.args.get("hub.mode")=="subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token")== "braba" :
            return "Erro de verificação de token", 403
        return request.args["hub.challenge"],200
    return "funcionando", 200


@app.route("/", methods=['POST'])
def webhook():
    data = request.get_json()
    log(data)

    if data['object'] =='page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']

                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else :
                        messaging_text= 'no text'
                    response = messaging_text
                    bot.send_text_message(sender_id, response)

    return "ok",200


def log(message):
    print(message)
    sys.stdout.flush()


if __name__ == "__main__":
    app.run(debug =True, port =80)
    
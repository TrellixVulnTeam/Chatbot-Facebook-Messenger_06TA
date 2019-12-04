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
listener = ''


file = open("dadosIntencoesChatBot.txt", "r") 
CONVERSATION = 1

for x in file:
  classe, texto = x.split(" - ")
  intencaos.append(classe)
  corpus.append(texto.rstrip())

X = vectorizer.fit_transform(corpus)
y = np.array(intencaos)

model = tree.DecisionTreeClassifier() 
model.fit(X, y)

dicionario = {
  'num':[ '1', '2', '3', '4', '5', '6', '7', '8',  '9', '10', "um", 'dois', 'tres','quatro', 'cinco','seis','sete', 'oito',  'nove', 'dez', 'uma', 'duas'],
  'opcoes':['Açúcar e canela','Acucar e canela','Açucar e canela','Açúcar com canela','Acucar com canela','Açucar com canela', 'Banana com Açúcar','Banana com Acucar','Banana com Açucar', 'Cheddar','chedar', 'Chocolate branco', 'Chocolate com avelã','Chocolate com avela', 'Coco com açúcar','Coco com acucar','Coco com açucar', 'Doce de leite', 'Dog', 'Napolitano', 'Ovomaltine com Chocolate', 'Pepperoni','peperoni', 'Pizza', 'Queijo Parmesão','queijo parmesao', 'Requeijão','requeijao', 'Salsa']
}

def reconhece_entidades(entrada):
      entidades = {}
      entrada = entrada.replace(',','')
      for key in dicionario.keys():
        for value in dicionario.get(key):
          if value.lower() in entrada.lower():
            values =[]
            if entidades.get(key) != None:
              for val in entidades.get(key):
                values.append(val)
            values.append(value)            
            entidades[key] = values

      return entidades

def classificador_de_intencoes(text):
    return model.predict(vectorizer.transform([text]))

def pedidos(quantidade, produto):
  verifica = 0
  for i in pedido:
    if i[0] == produto:
      i[1] = str(int(i[1])+int(quantidade))
      verifica = 1
  if verifica == 0:
    pedido.append([produto, quantidade])

def validador_endereco(endereco):
    return 1

def return_message(user_input):
    intencao = classificador_de_intencoes(user_input)
    if intencao == 'saudacao':
      return 'Ola, em que posso ajudar?'

    elif intencao == 'cardapio':
      return 'Nossas Opções são Pretzels de: \n- Açúcar e canela, \n- Banana com Açúcar, \n- Cheddar, \n- Chocolate, \n- Chocolate branco, \n- Chocolate com avelã, \n- Coco com açúcar, \n- Doce de leite, \n- Napolitano, \n- Ovomaltine com Chocolate, \n- Pepperoni, \n- Pizza, \n- Queijo Parmesão, \n- Requeijão, \n- Salsa \n- Quais desses você gostaria de comprar?'
    
    elif intencao == 'pedido':
        entidades = reconhece_entidades(user_input)
        for index, quantidade in enumerate(entidades['num']):
            pedidos(quantidade, entidades['opcoes'][index])
        listener ='passou_pedido'
        return ' Ok anotado! Gostaria de mais alguma coisa?'
        
    elif intencao == 'resposta_positiva' and listener == 'passou_pedido':
        return 'Ok, Qual voce gostaria?'

    elif intencao =='resposta_negativa' and listener == 'passou_pedido':
        retorno ='Apenas para confirmar, o pedido vai ser'
    
        for index, quantidade in enumerate(pedido):
          retorno += ' '+ pedido[index][1] +' Pretzels de ' + pedido[index][0]
          retorno += (' e' if index == qtd-2 else ',')
        retorno += ' certo?'
        listener = 'ok'
        return retorno

    elif intencao =='resposta_negativa' and listener == 'ok':
        return 'Entao acho que me confundi. Qual vai ser o pedido?'

    elif intencao == 'resposta_positiva' and listener == 'ok':
          return ' O pedido ficou R$price \n Qual vai ser a forma de pagamento? Dinheiro ou cartão?'

    elif intencao == 'forma_de_pagamento' and len(pedido) > 0:
        listener = 'endereco'
        return 'Tudo bem! E qual vai ser o endereço de entrega?'
    elif intencao == 'cancelamento_pedido':
        pedido.clear()
        listener =''
        return  'Pedido cancelado com sucesso'
    #elif listener == 'endereco':
    #    return 'Ok, anotado! \n- Muito obrigado pelo pedido, ele chegará em alguns minutos'
        

    
    else:
      return  'Desculpe, eu não entendi! \nVocê pode repetir por favor?'


TOKEN_PAGE= "EAAGfWvt5cFABABZBFY3NL9JHFKEYn9dwswgCDgZAZA2DIDRL8fysezOqZCZAGbuOiKLkeKebNtrASCHODKFkefZAnK0chi3YpZAj0VUgHYqfN49mFUeFAn9ZA7eLvARngJ2SE2SzLR2Dh3h66NhyXM2ydafMvCY7ZAWQI8BLYWZAUKux4wbKielMbU"
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

    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                recipient_id = messaging_event['recipient']['id']

                if messaging_event.get('message'):
                    if 'text' in messaging_event['message']:
                        messaging_text = messaging_event['message']['text']
                    else :
                        messaging_text= 'no text'
                        
                    response = return_message(messaging_text)
                    bot.send_text_message(sender_id, response)

    return "ok",200


def log(message):
    print(message)
    sys.stdout.flush()


if __name__ == "__main__":
    app.run(debug =True, port =80)
    
import requests
import datetime
import os.path
import configparser
import json
from scheduler import book_timeslot
import re
try:
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read(os.path.dirname(os.path.realpath(__file__))+"/settings.ini")  # читаем конфиг
    api_key = config["Main"]["Token"]
    allowed_chat = config["Users"]["AllowedUsers"]
    email = config["Users"]["AllowedMail"]
    print('settings.ini succesfully loaded')
except Exception as e:
    print(e)

#получение последнего сообщения
def getLastMessage():
    url = "https://api.telegram.org/bot" + str(api_key) + "/getUpdates?limit=1&offset=-1"
    response = requests.get(url)
    data = response.json()
    with open('data.json', 'w') as file:
         json.dump(data, file)
    if re.search('callback_query', str(data)):
        messageType = 'query'
        chat_id = data['result'][len(data['result']) - 1]['callback_query']['from']['id']
        update_id = data['result'][len(data['result']) - 1]['update_id']
        message_text = data['result'][len(data['result']) - 1]['callback_query']['data']
        return messageType, update_id, chat_id, message_text
    elif re.search('message', str(data)):
        messageType = 'text'
        message_text = data['result'][len(data['result']) - 1]['message']['text']
        chat_id = data['result'][len(data['result']) - 1]['message']['chat']['id']
        update_id = data['result'][len(data['result']) - 1]['update_id']
        return messageType, update_id, chat_id, message_text
    else:
        messageType = 'other'
        update_id = '0'
        return messageType, update_id

#отправка сообщения в чат
def sendMessage(chat_id, text_message, markup_text=''):
    key = json.JSONEncoder().encode(markup_text)
    if markup_text == '':
        reply_markup = ''
    else:
        reply_markup = '&reply_markup=' + key
    url = 'https://api.telegram.org/bot' + str(api_key) + '/sendmessage?chat_id=' + str(chat_id) + '&text=' + str(
        text_message) + reply_markup
    response = requests.get(url)
    return response

#проверка что заполнены все критичные данные события
def eventCheck(event):
    if event.get('name') !='' and event.get('date') !='' and event.get('time') !='' and event.get('long') !=''  :
        return True
    else:
        return False

#Отображение инфы о событии и кнопки добавить и сброс
def showEventInfo(chat_id, event):
    text_message = 'Добавляемое событие '
    if event.get('name') !='':
        text_message = text_message + '"' + event.get('name') + '" '
    if event.get('date') !='':
        text_message = text_message + str(event.get('date')) +' '
    if event.get('time') !='':
        text_message = text_message + 'в ' + str(event.get('time')) +' '
    if event.get('long') !='':
        text_message = text_message + ' на ' + str(event.get('long')) +' ч '
    if event.get('comment') !='':
        text_message = text_message + 'с описанием: ' + str(event.get('comment'))
    inline_keyboard = {'inline_keyboard': [
        [{'text': 'Сброс', 'callback_data': 'reset'}, {'text': 'Создать', 'callback_data': 'create'}],
    ]}
    sendMessage(chat_id, text_message, inline_keyboard)

def setEvent(chat_id, event, email):
    sendMessage(chat_id, "Внесение события…")
    response = book_timeslot(event.get('name'), str(event.get('date')), event.get('time'), event.get('long'), event.get('comment'), email)
    if response == True:
        sendMessage(chat_id,'Событие "' + event.get('name') + '" добавлено, состоится ' + str(event.get('date')) + ' в ' + str(event.get('time')))
        mode = 'start'
    else:
        sendMessage(chat_id, "Ошибка добавления")
        mode = 'name'
    return mode

#Основное меню бота
def showMainMenu(chat_id, event, eventReady):
    comment_message = 'описание '
    if event.get('comment') != '':
        comment_message = comment_message + ' →'
    long_message = 'длина '
    if event.get('long') != '':
        long_message = long_message + event.get('long') + ' ч'

    if event.get('name') != '':
        if eventReady:
            text_message = 'Добавить параметры события ' + event.get('name')
            inline_keyboard = {'inline_keyboard': [
                [{'text': 'дата ' + event.get('date'), 'callback_data': 'EventDate'},
                {'text': 'время ' + event.get('time'), 'callback_data': 'EventTime'}],
                [{'text': long_message, 'callback_data': 'EventLong'},
                {'text': comment_message, 'callback_data': 'EventComment'}],
                [{'text': 'Сброс', 'callback_data': 'EventReset'}, {'text': 'Изменить название', 'callback_data': 'EventName'}],
                [{'text': 'Сохранить', 'callback_data': 'EventSet'},],
            ]}
        else:
            text_message = 'Добавить параметры события ' + event.get('name')
            inline_keyboard = {'inline_keyboard': [
                [{'text': 'дата ' + event.get('date'), 'callback_data': 'EventDate'},
                {'text': 'время ' + event.get('time'), 'callback_data': 'EventTime'}],
                [{'text': long_message, 'callback_data': 'EventLong'},
                {'text': comment_message, 'callback_data': 'EventComment'}],
                [{'text': 'Сброс', 'callback_data': 'EventReset'}, {'text': 'Изменить название', 'callback_data': 'EventName'}],
            ]}

    else:
        text_message = 'Введите название события:'
        inline_keyboard = ''# inline_keyboard = {'inline_keyboard': [

    sendMessage(chat_id, text_message, inline_keyboard)


#общий цикл
def run():
    event = {'name':'', 'date': '', 'time': '', 'long':'', 'comment':''}
    update_id = 0
    mode = 'start'
    while True:
        messageType = getLastMessage()[0]
        # если новое сообщение прилетело
        if update_id != getLastMessage()[1] and messageType in ['text','query']:
            messageType, update_id, chat_id, message_text = getLastMessage()

            if chat_id != int(allowed_chat):
                sendMessage(chat_id, 'You are not allowed')
            elif message_text == '/start':
                mode = 'start'
                message_text = ''
            elif message_text == '/cancel':
                mode = 'start'
                message_text = ''
            elif message_text == '/help':
                sendMessage(chat_id, 'Write @kennich')
                message_text = ''
            elif messageType == 'query':
                if message_text == 'Cancel':
                    mode = 'menu'
                if message_text == 'EventReset':
                    mode = 'start'
                elif message_text == 'EventName':
                    mode = 'name'
                elif message_text == 'EventDate':
                    mode = 'date'
                elif message_text == 'EventTime':
                    mode = 'time'
                elif message_text == 'EventLong':
                    mode = 'long'
                elif message_text == 'EventComment':
                    mode = 'comment'
                elif message_text == 'EventSet':
                    mode = 'set'


            # if mode != 'menu':
            #     sendMessage(chat_id, mode)

            if mode == 'start':

                event = {'name': '', 'date': '', 'time': '', 'long': '', 'comment': ''}
                mode = 'name'

            if mode == 'name':
                #print(message_text)
                if messageType == 'text' and message_text != '':
                    event.update(name=message_text)
                    mode = 'menu'
                else:
                    if event.get('name') != '':
                        inline_keyboard = {'inline_keyboard': [
                        [{'text': '← Назад', 'callback_data': 'Cancel'}],
                        ]}
                        sendMessage(chat_id, 'Текущее название: ' + event.get('name') + '. Изменить?', inline_keyboard)
                    else:
                        sendMessage(chat_id, 'Введите название добавляемого события:')

            elif mode == 'date':
                if messageType == 'text' and message_text != '':
                    event.update(date=message_text)
                    mode = 'menu'
            elif mode == 'time':
                if messageType == 'text' and message_text != '':
                    event.update(time=message_text)
                    mode = 'menu'
            elif mode == 'long':
                if messageType == 'text' and message_text != '':
                    event.update(long=message_text)
                    mode = 'menu'
                if messageType == 'query':
                    event.update(long='1')
            elif mode == 'comment':
                if messageType == 'text' and message_text != '':
                    event.update(comment=message_text)
                    mode = 'menu'
                else:
                    if event.get('comment') != '':
                        inline_keyboard = {'inline_keyboard': [
                            [{'text': '← Назад', 'callback_data': 'Cancel'}],
                        ]}
                        sendMessage(chat_id, 'Текущее описание: ' + event.get('comment') + '. Изменить?', inline_keyboard)
                    else:
                        sendMessage(chat_id, 'Введите описание добавляемого события:')
            elif mode == 'set':
                setEvent(chat_id, event, email)


            if mode == 'menu':
                # if event.get('name') == '':
                #     event.update(name=message_text)
               eventReady = eventCheck(event)
               showMainMenu(chat_id, event, eventReady) #eventCheck(event))






if __name__ == "__main__":
    run()
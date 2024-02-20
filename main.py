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
    email = 'test'
    print('settings.ini succesfully loaded')
except Exception as e:
    print(e)
start_time = datetime.datetime.now()
start_time = str(start_time+ datetime.timedelta(hours=3))
user_mode = {}

#получение последнего сообщения
def getLastMessage():

    url = "https://api.telegram.org/bot" + str(api_key) + "/getUpdates?limit=1&offset=-1"
    response = requests.get(url)
    data = response.json()

    #with open('data.json', 'w') as file:
    #    json.dump(data, file)
    if re.search('document', str(data)):
        messageType = 'document'
        chat_id = data['result'][len(data['result']) - 1]['message']['chat']['id']
        file_id = data['result'][len(data['result']) - 1]['message']['document']['file_id']

#https:// api.telegram.org / bot5855042022: AAECakCVuC9qFPxjO8GHXxvvstr2cKTNOd4 / getFile?file_id = BQACAgIAAxkBAAIEwmXTJsY7zRo6hY2e2HlA9jgoWmI7AAKBQAAChzaZSio2WxESRKakNAQ
        file_url = 'https://api.telegram.org/bot' + str(api_key) + '/getFile?file_id='+file_id
        response = requests.get(file_url)
        file_data = response.json()
        file_url = 'https://api.telegram.org/file/bot'+str(api_key)+'/'+file_data['result']['file_path']
        response = requests.get(file_url)
        with open(str(chat_id) + '.token.pickle', 'wb') as file:
            file.write(response.content)
        chat_id = data['result'][len(data['result']) - 1]['message']['chat']['id']
        update_id = data['result'][len(data['result']) - 1]['update_id']
        return messageType, update_id, chat_id
    elif re.search('callback_query', str(data)):
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

def setDate(chat_id):
    text_message = 'Выберите дату'
    current_date = datetime.datetime.now()
    keyboard = {'inline_keyboard': [
            [{'text': 'Сегодня','callback_data': str(current_date.date())}, {'text': 'Завтра','callback_data': str(current_date.date()+ datetime.timedelta(days=1))}],
            #[{'text': 'В пн'}, {'text': 'В сб'}]
        ]}
    response = sendMessage(chat_id, text_message, keyboard)
    return response

def setTime(chat_id,selected_date=''):
    text_message = 'Выберите время или введите вручную'
    current_time = datetime.datetime.now()
    current_date = datetime.date.today()

    if current_date == selected_date:
       current_hour = str(current_time)[11:13]
    else:
        current_hour = 0
    # ----------- Chunk of if statement to determine which inline keyboard to reply user ----------------
    if int(current_hour) < 8:
        keyboard = {'inline_keyboard': [
            [{'text': '08:00', 'callback_data': '08:00'}, {'text': '10:00', 'callback_data': '10:00'}],
            [{'text': '12:00', 'callback_data': '12:00'}, {'text': '14:00', 'callback_data': '14:00'}],
            [{'text': '16:00', 'callback_data': '16:00'}, {'text': '18:00', 'callback_data': '18:00'}],
            [{'text': '20:00', 'callback_data': '20:00'}, {'text': '22:00', 'callback_data': '22:00'}],
        ]}
    elif 8 <= int(current_hour) < 10:
        keyboard = {'inline_keyboard': [
            [{'text': '10:00'}],
            [{'text': '12:00'}], [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 10 <= int(current_hour) < 12:
        keyboard = {'inline_keyboard': [
            [{'text': '12:00'}], [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 12 <= int(current_hour) < 14:
        keyboard = {'inline_keyboard': [
            [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 14 <= int(current_hour) < 16:
        keyboard = {'inline_keyboard': [
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 16 <= int(current_hour) < 18:
        keyboard = {'inline_keyboard': [
            [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 18 <= int(current_hour) < 20:
        keyboard = {'inline_keyboard': [
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 20 <= int(current_hour) < 22:
        keyboard = {'inline_keyboard': [
            [{'text': '22:00'}],
        ]}
    else:
        return sendMessage(chat_id, 'Выберите другой день')
    response = sendMessage(chat_id, text_message, keyboard)
    return response

def setLong(chat_id):
    text_message = 'Выберите продолжительность'
    keyboard = {'inline_keyboard': [
            [{'text': '1 час','callback_data': '1'}, {'text': '2 часа','callback_data': '2'}],
            [{'text': '4 часа', 'callback_data': '4'}, {'text': '8 часов', 'callback_data': '8'}],
        ]}
    response = sendMessage(chat_id, text_message, keyboard)
    return response

def parseTime(input_text):
    input_text = re.sub('\D', ':', input_text)
    timestring = ''

    state = 'false'
    if re.fullmatch('[0-2]?[0-9]:[0-5][0-9]', input_text):
        timestring=re.findall('[0-2]?[0-9]:[0-5][0-9]', input_text)[0]
        state = 'true'
    elif re.search('[0-2]?[0-9]', input_text):
        timestring= re.findall('[0-2]?[0-9]', input_text)[0] + ':00'
        state = 'true'
    elif re.search('[0-9]?[0-9]?[0-9]', input_text):
        timestring='00:'+re.findall('[0-9]?[0-9]?[0-9]', input_text)[0]
        state = 'true'
    print(timestring)
    return state, timestring

def parseDate(input_text):
    #символы одни
    state = 'false'
    input_text = re.sub('\D', '.', input_text)
    date_pattern = '\d{1,2}.\d\d.?\d{0,4}' # 11.22.3333
    input_words = re.split(r' ', input_text)
    date = re.search(date_pattern, input_text)

    datestring = re.search(date_pattern, input_text)
    input_string = re.sub(date_pattern, '', input_text)
    #print(datestring[0] if datestring else 'Not found')
    if datestring:
        state = 'true'
    return state, datestring[0]

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

def setEvent(chat_id, event):
    sendMessage(chat_id, "Внесение события…")
    response = book_timeslot(event.get('name'), str(event.get('date')), event.get('time'), event.get('long'), event.get('comment'), chat_id)
    if response == True:
        sendMessage(chat_id,'Событие "' + event.get('name') + '" добавлено, состоится ' + str(event.get('date')) + ' в ' + str(event.get('time')))
        mode = 'start'
    else:
        sendMessage(chat_id, "Ошибка добавления")
        mode = 'menu'
    return mode

#Основное меню бота
def showMainMenu(chat_id, event, eventReady):
    comment_message = 'Описание '
    if event.get('comment') != '':
        comment_message = comment_message + ' →'
    long_message = 'Длина '
    if event.get('long') != '':
        long_message = long_message + event.get('long') + ' ч'

    if event.get('name') != '':
        if eventReady:
            text_message = 'Измените параметры события ' + event.get('name')
            inline_keyboard = {'inline_keyboard': [
                [{'text': 'Дата ' + event.get('date'), 'callback_data': 'EventDate'},
                {'text': 'Время ' + event.get('time'), 'callback_data': 'EventTime'}],
                [{'text': long_message, 'callback_data': 'EventLong'},
                {'text': comment_message, 'callback_data': 'EventComment'}],
                [{'text': 'Сброс', 'callback_data': 'EventReset'}, {'text': 'Изменить название', 'callback_data': 'EventName'}],
                [{'text': 'Создать событие', 'callback_data': 'EventSet'},],
            ]}
        else:
            text_message = 'Измените параметры события ' + event.get('name')
            inline_keyboard = {'inline_keyboard': [
                [{'text': 'Дата ' + event.get('date'), 'callback_data': 'EventDate'},
                {'text': 'Время ' + event.get('time'), 'callback_data': 'EventTime'}],
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
    event = {'name':'', 'date': '', 'time': '', 'long':'1', 'comment':''}
    user_event = {}
    update_id = getLastMessage()[1]
    #mode = 'start'
    while True:
        messageType = getLastMessage()[0]
        # если новое сообщение прилетело
        if update_id != getLastMessage()[1] and messageType in ['text','query']:
            messageType, update_id, chat_id, message_text = getLastMessage()
            if chat_id not in user_mode:
                user_mode[chat_id] = 'start'
                user_event[chat_id] = event

            if message_text == '/start':
                user_mode[chat_id] = 'start'
                message_text = ''
            elif message_text == '/ontime':
              sendMessage(chat_id, 'Бот запущен: '+str(start_time))
              message_text = ''
            elif message_text == '/delete_me':
                if os.path.exists(str(chat_id) + '.token.pickle'):
                    os.remove(str(chat_id) + '.token.pickle')
                sendMessage(chat_id, 'Данные авторизации удалены')
                message_text = ''
            elif message_text == '/cancel':
                user_mode[chat_id] = 'start'
                message_text = ''
            elif message_text == '/help':
                sendMessage(chat_id, 'Write @kennich')
                message_text = ''
            elif messageType == 'query':
                if message_text == 'Cancel':
                    user_mode[chat_id] = 'menu'
                if message_text == 'EventReset':
                    user_mode[chat_id] = 'start'
                elif message_text == 'EventName':
                    user_mode[chat_id] = 'name'
                elif message_text == 'EventDate':
                    user_mode[chat_id] = 'date'
                elif message_text == 'EventTime':
                    user_mode[chat_id] = 'time'
                elif message_text == 'EventLong':
                    user_mode[chat_id] = 'long'
                elif message_text == 'EventComment':
                    user_mode[chat_id] = 'comment'
                elif message_text == 'EventSet':
                    user_mode[chat_id] = 'set'


            # if user_mode[chat_id] != 'menu':
            #     sendMessage(chat_id, mode)

            if user_mode[chat_id] == 'start':

                user_event[chat_id] = {'name': '', 'date': '', 'time': '', 'long': '1', 'comment': ''}
                user_mode[chat_id] = 'name'
            if user_mode[chat_id] == 'name':

                if messageType == 'text' and message_text != '':
                    user_event[chat_id].update(name=message_text)
                    user_mode[chat_id] = 'menu'
                else:
                    if user_event[chat_id]['name'] != '':
                        inline_keyboard = {'inline_keyboard': [
                        [{'text': '← Назад', 'callback_data': 'Cancel'}],
                        ]}
                        sendMessage(chat_id, 'Текущее название: ' + user_event[chat_id].get('name') + '. Изменить?', inline_keyboard)
                    else:
                        sendMessage(chat_id, 'Введите название добавляемого события:')

            elif user_mode[chat_id] == 'date':
                if messageType == 'text' and message_text != '':
                    if parseDate(message_text)[0]:
                        user_event[chat_id].update(date=parseDate(message_text)[1])
                        user_mode[chat_id] = 'menu'
                elif messageType == 'query' and message_text != 'EventDate':
                    user_event[chat_id].update(date=message_text)
                    user_mode[chat_id] = 'menu'
                else:
                    setDate(chat_id)
            elif user_mode[chat_id] == 'time':
                if messageType == 'text' and message_text != '':
                    if parseTime(message_text)[0]:
                        user_event[chat_id].update(time=parseTime(message_text)[1])
                        user_mode[chat_id] = 'menu'
                elif messageType == 'query' and message_text != 'EventTime':
                    user_event[chat_id].update(time=message_text)
                    user_mode[chat_id] = 'menu'
                else:
                    setTime(chat_id, user_event[chat_id].get('date'))

            elif user_mode[chat_id] == 'long':
                if messageType == 'text' and message_text != '':
                    if parseTime(message_text)[0]:
                        user_event[chat_id].update(long=parseTime(message_text)[1])
                        user_mode[chat_id] = 'menu'
                    else:
                        setLong(chat_id)
                elif messageType == 'query' and message_text != 'EventLong':
                    user_event[chat_id].update(long=message_text)
                    user_mode[chat_id] = 'menu'
                else:
                    setLong(chat_id)
            elif user_mode[chat_id] == 'comment':
                if messageType == 'text' and message_text != '':
                    user_event[chat_id].update(comment=message_text)
                    user_mode[chat_id] = 'menu'
                else:
                    if user_event[chat_id].get('comment') != '':
                        inline_keyboard = {'inline_keyboard': [
                            [{'text': '← Назад', 'callback_data': 'Cancel'}],
                        ]}
                        sendMessage(chat_id, 'Текущее описание: ' + user_event[chat_id].get('comment') + '. Изменить?', inline_keyboard)
                    else:
                        sendMessage(chat_id, 'Введите описание добавляемого события:')
            elif user_mode[chat_id] == 'set':
                if setEvent(chat_id, user_event[chat_id]):
                    user_mode[chat_id] = 'start'
                else:
                    user_mode[chat_id] = 'menu'

            if user_mode[chat_id] == 'menu':
               eventReady = eventCheck(user_event[chat_id])
               showMainMenu(chat_id, user_event[chat_id], eventReady) #eventCheck(event))

if __name__ == "__main__":
    run()
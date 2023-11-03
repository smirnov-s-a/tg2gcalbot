import requests
import datetime
import os.path
import configparser
import json
from scheduler import book_timeslot
import re
# create a python file called api_key
# that contains a dictionary api={"api_key":"your_api_key"}
try:
    config = configparser.ConfigParser()  # создаём объекта парсера
    config.read(os.path.dirname(os.path.realpath(__file__))+"/settings.ini")  # читаем конфиг
    api_key = config["Main"]["Token"]
    # Path = config["Main"]["Path"]
    allowed_chat = config["Users"]["AllowedUsers"]
    email = config["Users"]["AllowedMail"]
    # MessageStarted = config["Messages"]["MessageStarted"]
    # MessageSaved = config["Messages"]["MessageSaved"]
    # MessageError = config["Messages"]["MessageError"]
    # MessageNotAllowed = config["Messages"]["MessageNotAllowed"]
    print('settings.ini succesfully loaded')
except Exception as e:
    print(e)

def getLastMessage():
    url = "https://api.telegram.org/bot" + str(api_key) + "/getUpdates?limit=1&offset=-1"
    response = requests.get(url)

    data = response.json()
    with open('data.json', 'w') as file:
        json.dump(data, file)

    try:
        last_msg = data['result'][len(data['result']) - 1]['message']['text']
        chat_id = data['result'][len(data['result']) - 1]['message']['chat']['id']
        update_id = data['result'][len(data['result']) - 1]['update_id']

    except:
        last_msg =''
        chat_id =''
        update_id = ''

        callback_query_id =  data['result'][len(data['result']) - 1]['callback_query']['id']

        if sendCallbackQuery(api_key, callback_query_id, 'date'):


    return last_msg, chat_id, update_id


def sendMessage(chat_id, text_message):
    url = 'https://api.telegram.org/bot' + str(api_key) + '/sendMessage?text=' + str(text_message) + '&chat_id=' + str(
        chat_id)
    response = requests.get(url)
    return response

def sendMessageWithMarkup(chat_id, text_message, markup_text):
    key = json.JSONEncoder().encode(markup_text)
    url = 'https://api.telegram.org/bot' + str(api_key) + '/sendmessage?chat_id=' + str(chat_id) + '&text=' + str(
        text_message) + '&reply_markup=' + key
    response = requests.get(url)
    return response

def sendCallbackQuery(api_key, callback_query_id, text):
    url = 'https://api.telegram.org/bot' + str(api_key) + '/answerCallbackQuery?callback_query_id='+callback_query_id+'&text='+text
    response = requests.get(url)
    if re.search('200', str(response)):
        return True
    else:
        return False

def checkTime(text):
    regex = '^([01]\d|2[0-3]):?([0-5]\d)$'
    if (re.search(regex, text)):
        print("Valid Time")
        return True
    else:
        print("Invalid Time")
        return False

def checkDate(text):
    selectedDate=''

    if text in ['сегодня', 'Сегодня']:
        selectedDate = datetime.date.today()
        print(selectedDate)
    elif text in ['завтра', 'Завтра']:
        selectedDate = datetime.date.today() + datetime.timedelta(days=1)
        print(selectedDate)
    else:
        try:
            res = re.sub(r"[/\\.]", "-", re.search(r"(\d+.*?\d+.*?\d+)", text).group(1))
            print(res)
            selectedDate = res
        except:
            selectedDate=''

    return selectedDate

def checkEventReady(event):
    keys = event.keys()
    responce = True
    if '' in [event.get(key) for key in keys]:
        print("Invalid Event")
        responce = False
    if responce:
        print(" Valid  Event")
    return responce




def optionSelector(chat_id,event):
    text_message = 'Добавляемое событие "' + event.get('name') + '" ' + str(event.get('date')) + ' в ' + str(event.get('time'))

    inline_keyboard = {'inline_keyboard': [
            [{'text':'название', 'callback_data': 'string'},{'text':'описание', 'callback_data': 'string'}],
            [{'text':'дата', 'callback_data': 'data'},{'text':'время', 'callback_data': 'string'}],
            [{'text': 'Сброс', 'callback_data': 'string'}, {'text': 'Создать', 'callback_data': 'string'}],
        ]}

    key = json.JSONEncoder().encode(inline_keyboard)
    url = 'https://api.telegram.org/bot' + str(api_key) + '/sendmessage?chat_id=' + str(chat_id) + '&text=' + str(
        text_message) + '&reply_markup=' + key
    response = requests.get(url)

    data = response.json()
    with open('query.json', 'w') as file:
        json.dump(data, file)

        sendCallbackQuery(api_key, '417777293313465066', 'дата');

    return response


def sendInlineMessageForService(chat_id):
    text_message = 'Добавить событие в календарь!'

    inline_keyboard = {'inline_keyboard': [
            [{'text':'название', 'callback_data': 'string'},{'text':'описание', 'callback_data': 'string'}],
            [{'text':'дата', 'callback_data': 'string'},{'text':'время', 'callback_data': 'string'}],
        ]}

    key = json.JSONEncoder().encode(inline_keyboard)
    url = 'https://api.telegram.org/bot' + str(api_key) + '/sendmessage?chat_id=' + str(chat_id) + '&text=' + str(
        text_message) + '&reply_markup=' + key
    response = requests.get(url)
    return response



def sendInlineMessageForBookingDate(chat_id):
    text_message = 'Выберите дату'
    current_time = datetime.datetime.now()
    keyboard = {'keyboard': [
            [{'text': 'Сегодня'}, {'text': 'Завтра'}],
            [{'text': 'В пн'}, {'text': 'В сб'}]
        ]}

    key = json.JSONEncoder().encode(keyboard)
    url = 'https://api.telegram.org/bot' + str(api_key) + '/sendmessage?chat_id=' + str(chat_id) + '&text=' + str(
        text_message) + '&reply_markup=' + key
    response = requests.get(url)
    return response

def sendInlineMessageForBookingTime(chat_id,selectedDate):
    text_message = 'Выберите время или введите вручную'
    current_time = datetime.datetime.now()
    currentDate = datetime.date.today()

    if currentDate == selectedDate:
       current_hour = str(current_time)[11:13]
    else:
        current_hour = 0
    # ----------- Chunk of if statement to determine which inline keyboard to reply user ----------------
    if current_hour == 0:
        keyboard = {'keyboard': [
            [{'text': '08:00'}], [{'text': '10:00'}],
            [{'text': '12:00'}], [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    if int(current_hour) < 8:
        keyboard = {'keyboard': [
            [{'text': '08:00'}], [{'text': '10:00'}],
            [{'text': '12:00'}], [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 8 <= int(current_hour) < 10:
        keyboard = {'keyboard': [
            [{'text': '10:00'}],
            [{'text': '12:00'}], [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 10 <= int(current_hour) < 12:
        keyboard = {'keyboard': [
            [{'text': '12:00'}], [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 12 <= int(current_hour) < 14:
        keyboard = {'keyboard': [
            [{'text': '14:00'}],
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 14 <= int(current_hour) < 16:
        keyboard = {'keyboard': [
            [{'text': '16:00'}], [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 16 <= int(current_hour) < 18:
        keyboard = {'keyboard': [
            [{'text': '18:00'}],
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 18 <= int(current_hour) < 20:
        keyboard = {'keyboard': [
            [{'text': '20:00'}], [{'text': '22:00'}],
        ]}
    elif 20 <= int(current_hour) < 22:
        keyboard = {'keyboard': [
            [{'text': '22:00'}],
        ]}
    else:
        return sendMessage(chat_id, 'Выберите другой день')
        sendInlineMessageForBookingDate(chat_id)
    # ----------------------------------------------------------------------------------------------------
    key = json.JSONEncoder().encode(keyboard)
    url = 'https://api.telegram.org/bot' + str(api_key) + '/sendmessage?chat_id=' + str(chat_id) + '&text=' + str(
        text_message) + '&reply_markup=' + key
    response = requests.get(url)
    return response


def run():
    global allowed_chat
    event = {'date': '', 'time': '', 'name':''}

    try:
        prev_last_msg, chat_id, prev_update_id = getLastMessage()
    except:
        prev_last_msg = ''
        chat_id = ''
        prev_update_id = ''


    while True:
        #обновление сообщения
        try:
            current_last_msg, chat_id, current_update_id = getLastMessage()
        except:
            current_last_msg = prev_last_msg = ''
            current_update_id = prev_update_id

        #если нового сообщения нет
        if prev_last_msg == current_last_msg and current_update_id == prev_update_id:
            while prev_last_msg == current_last_msg and current_update_id == prev_update_id:
                current_last_msg, chat_id, current_update_id = getLastMessage()
                #print('waiting')
                #time.sleep(5)
            continue

        #проверка пользователя (чата)
        elif chat_id != int(allowed_chat):
            if current_last_msg != prev_last_msg:
                sendMessage(chat_id, "Unallowed!")
            continue
        #подцикл работ с командами и сообщениями
        else:
            #команды
            if current_last_msg == '/cancel':
                # return
                event = {'date': '', 'time': '', 'name': ''}
                continue

            elif current_last_msg == '/start':
                sendInlineMessageForService(chat_id)
                event = {'date': '', 'time': '', 'name': ''}
                print(chat_id)


            # фильтрация сообщений

            elif checkTime(current_last_msg) == True:
                event.update(time=current_last_msg)
                print("время есть")
                #booking_time = current_last_msg
                #update_id_for_booking_of_time_slot = current_update_id
                #sendMessage(chat_id, "Please enter email address:")


            elif checkDate(current_last_msg) != '':
                event.update(date=checkDate(current_last_msg))
                print("дата есть")

            else:
                event.update(name=current_last_msg)
                print("имя есть")
                #booking_time = current_last_msg
                #update_id_for_booking_of_time_slot = current_update_id
                #sendMessage(chat_id, "Please enter email address:")

            #event.get('description') = 'Created form telegram bot'






            #следующая итерация
            prev_last_msg = current_last_msg
            prev_update_id = current_update_id
    # запуск создания события если все данные есть


        if checkEventReady(event):
            sendMessage(chat_id, "Внесение события…")
            # sendMessage(chat_id, event.get('date'))
            response = book_timeslot(event.get('name'), str(event.get('date')), event.get('time'), event.get('description'),
                             email)
            if response == True:
                sendMessage(chat_id,
                        'Событие "' + event.get('name') + '" добавлено, состоится ' + str(
                            event.get('date')) + ' в ' + str(
                            event.get('time')))
                event = {'date': '', 'time': '', 'name': ''}
                continue
            else:

                sendMessage(chat_id, "Ошибка добавления")
                event = {'date': '', 'time': '', 'name': ''}
                continue
        else:
            if event.get('date') == '':
                sendInlineMessageForBookingDate(chat_id)
            elif event.get('time') == '':
                sendInlineMessageForBookingTime(chat_id, event.get('date'))
            else:
                optionSelector(chat_id, event)
                #sendMessage(chat_id, "Введите название события")





if __name__ == "__main__":
    run()
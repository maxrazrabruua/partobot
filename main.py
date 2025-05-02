import telebot
from telebot import types
import json
from security import token
import random
import time
import IBT_ai as ibt

bot = telebot.TeleBot(token)
USERY = "ЗДЕСЬ_ВАШ_ИД_ТГ"

def load(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        return json.load(file)

def save(filename, data):
    savedata = load(filename)
    with open(filename, 'w', encoding="utf-8") as file:
        try:
            json.dump(data, file, indent=4, ensure_ascii=False)
        except:
            save(filename, savedata)

@bot.message_handler(commands=['start'])
def start(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if not i in data["users"].keys():
        data["users"][i] = {
            "username": message.from_user.username,
            "banned": False,
            "status": {
                "president": False,
                "citizen": None
            }
        }
        save("data.json", data)
        bot.reply_to(message, "Вы наш новый участник группы партикло, теперь вы зарегистрированы!")
    else:
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        bot.reply_to(message, "Вы уже были зарегистрированы!")

@bot.message_handler(commands=['president'])
def president(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        bot.reply_to(message, f"Вы {'не ' if not data['users'][i]['status']['president'] else ''}президент")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['new'])
def new(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        if message.reply_to_message:
            if i == USERY:
                eu = str(message.reply_to_message.from_user.id)
                if eu in data["users"].keys():
                    if data['users'][eu]['banned']:
                        bot.reply_to(message, "Он ЗАБАНЕН!")
                        return
                    whopresident = None
                    for n, u in data["users"].items():
                        if u["status"]["president"]:
                            whopresident = n
                            break

                    if whopresident:
                        data["users"][whopresident]["status"]["president"] = False
                    data["users"][eu]["status"]["president"] = True
                    save("data.json", data)
                    bot.reply_to(message, f"Теперь сменился президент на @{data['users'][eu]['username']}!")
                else:
                    bot.reply_to(message, "Данный пользователь не зарегистрирован, попросите его зарегистрироваться!")
            else:
                bot.reply_to(message, "Вы не Ардиновец чтобы менять президенство")
        else:
            bot.reply_to(message, "Ответь на сообщение другого чтобы обозначить его президентсво!")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['reban'])
def reban(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if message.reply_to_message:
            if i == USERY or data["users"][i]["status"]["president"]:
                eu = str(message.reply_to_message.from_user.id)
                if eu in data["users"].keys():
                    if not (i == USERY or data["users"][i]["status"]["president"]):
                        data["users"][eu]["banned"] = not data["users"][eu]["banned"]
                        save("data.json", data)
                        bot.reply_to(message, f"Пользователь успешно {'за' if data['users'][eu]['banned'] else 'раз'}банен")
                    else:
                        bot.reply_to(message, "Нельзя ребанить президента или важную фигуру для государства")
                else:
                    bot.reply_to(message, "Данный пользователь не зарегистрирован, попросите его зарегистрироваться!")
            else:
                bot.reply_to(message, "Вы не президент(или же другое важное для государства лицо) чтобы ребанить")
        else:
            bot.reply_to(message, "Ответь на сообщение другого чтобы его ребанить!")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['create'])
def create(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        name = message.text[8:]
        if not name in data["cities"].keys():
            if message.chat.type == "supergroup":
                for city in data["cities"].values():
                    if city["chat"] == message.chat.id:
                        bot.reply_to(message, "Данный чат уже занимает город")
                        return
                data["cities"][name] = {
                    "chat": message.chat.id,
                    "autor": message.from_user.id,
                    "status": {
                        "alert": False,
                        "message": "Сообщение для жителей не выставлено"
                    }
                }
                data["users"][i]["status"]["citizen"] = name
                save("data.json", data)
                bot.reply_to(message, f"Новый город \"{name}\" был создан!")
            else:
                bot.reply_to(message, "Это НЕ группа!")
        else:
            bot.reply_to(message, "Такой город уже существует!")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['delete'])
def delete(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        if message.chat.type == "supergroup":
            n = ""
            for name, dat in data["cities"].items():
                if dat["chat"] == message.chat.id:
                    if dat["autor"] == message.from_user.id:
                        n = name
                        break
                    else:
                        bot.reply_to(message, "Вы не владелец данного города!")
                        return
            if n:
                for nu, vu in data["users"].items():
                    if not data["users"][nu]["banned"]:
                        if vu["status"]["citizen"] == n:
                            data["users"][nu]["status"]["citizen"] = None
                            try:
                                bot.send_message(int(nu), f"Город \"{n}\" был удалён, так что у вас нет больше с этого момента гражданства")
                            except:
                                data["users"][nu]["banned"] = True
                del data["cities"][n]
                save("data.json", data)
                bot.reply_to(message, f"Город \"{n}\" был удалён\nПрощай город!")
            else:
                bot.reply_to(message, "В этом чате нет подходящего города")
        else:
            bot.reply_to(message, "Это вообще не группа")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['rename'])
def rename(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        if message.chat.type == "supergroup":
            n = ""
            newname = message.text[8:]
            if newname:
                for name, dat in data["cities"].items():
                        if dat["chat"] == message.chat.id:
                            if dat["autor"] == message.from_user.id:
                                n = name
                                break
                            else:
                                bot.reply_to(message, "Вы не владелец данного города!")
                                return
                if n:
                    for nu, vu in data["users"].items():
                        if not data["users"][nu]["banned"]:
                            if vu["status"]["citizen"] == n:
                                data["users"][nu]["status"]["citizen"] = newname
                                try:
                                    bot.send_message(int(nu), f"Город \"{n}\" был перименнован в \"{newname}\"!")
                                except:
                                    data["users"][nu]["banned"] = True
                    data["cities"][newname] = data["cities"][n]
                    del data["cities"][n]
                    save("data.json", data)
                    bot.reply_to(message, f"Город \"{n}\" был переименован в \"{newname}\"!")
                else:
                    bot.reply_to(message, "В этом чате нет подходящего города")
            else:
                bot.reply_to(message, "Некорректное название чата")
        else:
            bot.reply_to(message, "Это вообще не группа")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['alertCheck', 'alertcheck'])
def alertCheck(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return

        text = f"----- КАРТА ТРЕВОГ -----\nУсловности:\n🟢 - нет тревоги\n🔴 - тревога\n{'-' * 37}\n"
        for name, city in data["cities"].items():
            text += f"{'🔴' if city['status']['alert'] else '🟢'} {name}: {city['status']['message']}\n"
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['setalert', 'setAlert'])
def setAlert(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        if message.chat.type == "supergroup":
            n = ""
            for name, dat in data["cities"].items():
                if dat["chat"] == message.chat.id:
                    if dat["autor"] == message.from_user.id:
                        n = name
                        break
                    else:
                        bot.reply_to(message, "Вы не владелец данного города!")
                        return
            if n:
                data["cities"][n]["status"]["alert"] = not data["cities"][n]["status"]["alert"]
                for nu, vu in data["users"].items():
                    if not data["users"][nu]["banned"]:
                        if vu["status"]["citizen"] == n:
                            try:
                                bot.send_message(int(nu), "ТРЕВОГА! БУДЬТЕ ОККУРАТНЫ С ВСЯКИМИ ВРАГАМИ!" if data["cities"][n]["status"]["alert"] else "Отбой тревоги, отбой тревоги!")
                            except:
                                data["users"][nu]["banned"] = True
                save("data.json", data)
                bot.reply_to(message, "ТРЕВОГА! БУДЬТЕ ОКУКРАТНЫ С ВСЯКИМИ ВРАГАМИ!" if data["cities"][n]["status"]["alert"] else "Отбой тревоги, отбой тревоги!")
            else:
                bot.reply_to(message, "В этом чате нет подходящего города")
        else:
            bot.reply_to(message, "Это вообще не группа")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['citizen'])
def citizen(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        if message.chat.type == "supergroup":
            n = ""
            for name, dat in data["cities"].items():
                if dat["chat"] == message.chat.id:
                    n = name
                    break
            if n:
                if data["users"][i]['status']['citizen'] == n:
                    data["users"][i]['status']['citizen'] = None
                    bot.reply_to(message, "Вы успешно удалили своё гражданство")
                else:
                    data["users"][i]['status']['citizen'] = n
                    bot.reply_to(message, "Поздравляю с новым гражданством!")
                save("data.json", data)
            else:
                bot.reply_to(message, "В этом чате нет подходящего города")
        else:
            bot.reply_to(message, "Это вообще не группа")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

def getemoji() -> str:
    data = load("data.json")
    return random.choice(list(data["emoji"]))

def generator():
    data = load("data.json")
    code = ""
    while True:
        code = ""
        for _ in range(4):
            code += getemoji()
        if not code in data['generaty'].keys():
            break
    return code

@bot.message_handler(commands=['view'])
def view(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        
        code = generator()
        realtime = time.time()
        now = time.localtime()
        t = time.strftime("%Y-%m-%d %H:%M:%S по киевскому времени", now)
        text = f'{"-" * 5} ГРАЖДАНСТВО {"-" * 5}\nВаше гражданство здесь: {data["users"][i]["status"]["citizen"]}\n{"-" * 37}\nКод индефикации: {code}\nВремя: {t}'
        data["generaty"][code] = {
            "id": i,
            "time": t,
            "realtime": realtime
        }
        save("data.json", data)
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['check'])
def check(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        code = message.text[7:]
        if len(code) == 4:
            if code in data["generaty"].keys():
                if data["generaty"][code]['id'] in data["users"].keys():
                    bot.reply_to(message, "\n".join([
                        "ИНФО:",
                        f"Ид гражданина: {data['generaty'][code]['id']}",
                        f"Юзернейм(на базе): @{data['users'][data['generaty'][code]['id']]['username']}",
                        f"Город выдачи: {data['users'][data['generaty'][code]['id']]['status']['citizen']}",
                        f"Время выдачи(читабельный формат): {data['generaty'][code]['time']}",
                        f"Время выдачи(программированный формат): {data['generaty'][code]['realtime']}"
                    ]))
                else:
                    bot.reply_to(message, "Данный пользователь не зарегистрирован, попросите его зарегистрироваться!")
            else:
                bot.reply_to(message, "Либо такой выдачи гражданства не существует либо подделан!")
        else:
            bot.reply_to(message, "Некорректная длина для кода!")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['stata'])
def stata(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        name = message.text[7:]
        if name:
            if name in data["cities"].keys():
                people = 0
                for u in data['users'].values():
                    if u["status"]["citizen"] == name:
                        people += 1
                city = data["cities"][name]
                bot.reply_to(message, "\n".join([
                    f"{'-' * 36}\n",
                    f"Город: {name}",
                    f"Ид владельца: {city['autor']}",
                    f"Юзернейм владельца: @{data['users'][str(city['autor'])]['username']}",
                    f"Ид чата: {city['chat']}\n",
                    f"Статусы:",
                    f"Тревога: {'🔴' if city['status']['alert'] else '🟢'}",
                    f"Сообщение для граждан: {city['status']['message']}\n",
                    f"Граждан живут: {people}",
                    f"{'-' * 36}"
                ]))
            else:
                bot.reply_to(message, "Такого города не существует!")
        else:
            if message.chat.type == "supergroup":
                n = ''
                for name, dat in data["cities"].items():
                    if dat["chat"] == message.chat.id:
                        n = name
                        break
                if n:
                    city = data["cities"][n]
                    people = 0
                    for u in data['users'].values():
                        if u["status"]["citizen"] == name:
                            people += 1
                    city = data["cities"][name]
                    bot.reply_to(message, "\n".join([
                        f"{'-' * 36}\n",
                        f"Город: {name}",
                        f"Ид владельца: {city['autor']}",
                        f"Юзернейм владельца: @{data['users'][str(city['autor'])]['username']}",
                        f"Ид чата: {city['chat']}\n",
                        f"Статусы:",
                        f"Тревога: {'🔴' if city['status']['alert'] else '🟢'}",
                        f"Сообщение для граждан: {city['status']['message']}\n",
                        f"Граждан живут: {people}",
                        f"{'-' * 36}"
                    ]))
                else:
                    bot.reply_to(message, "Не существует такого города")
            else:
                bot.reply_to(message, "Это не группа!")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['message'])
def message(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        if message.chat.type == "supergroup":
            n = ""
            info = message.text[9:]
            if not info:
                info = "Сообщение для жителей не выставлено"
            for name, dat in data["cities"].items():
                if dat["chat"] == message.chat.id:
                    if dat["autor"] == message.from_user.id:
                        n = name
                        break
                    else:
                        bot.reply_to(message, "Вы не владелец данного города!")
                        return
            if n:
                data["cities"][n]["status"]["message"] = info
                for nu, vu in data["users"].items():
                    if not data["users"][nu]["banned"]:
                        if vu["status"]["citizen"] == n:
                            try:
                                bot.send_message(int(nu), f"Инфа уточнена: '{info}'")
                            except:
                                data["users"][nu]["banned"] = True
                save("data.json", data)
                bot.reply_to(message, f"Инфа уточнена: '{info}'")
            else:
                bot.reply_to(message, "В этом чате нет подходящего города")
        else:
            bot.reply_to(message, "Это вообще не группа")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['const'])
def const(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        constitut = load("constitution.json")
        bot.reply_to(message, f"Всего страниц в конституции: {len(constitut.keys())}\n/delrage <rage: num / name> - удалить страницу конституции\n/viewrage <rage: num / name> - просмотр указанной страницы\n/rages - просмотр страниц с заголовком(num - name)\n/add <name>; <text>")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

def isnum(x: str):
    try:
        int(x)
        return True
    except:
        return False

@bot.message_handler(commands=['delrage'])
def delrage(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        constitut = load("constitution.json")
        if data['users'][i]['president'] or i == USERY:
            if message.text[9:]:
                if isnum(message.text[9:]):
                    try:
                        del constitut[message.text[9:]]
                        save("constitution.json", constitut)
                        bot.reply_to(message, "Страница конституции была удалена успешно!")
                    except:
                        bot.reply_to(message, "Такого номера страницы не существует!")
                else:
                    yes = ''
                    for name, value in constitut.items():
                        if value['name'] == message.text[9:]:
                            yes = name
                            break
                    if yes:
                        del constitut[name]
                        save("constitution.json", constitut)
                        bot.reply_to(message, "Страница конституции была удалена успешно!")
                    else:
                        bot.reply_to(message, "Такой страницы не существует!")
            else:
                bot.reply_to(message, "Аргумент пуст")
        else:
            bot.reply_to(message, "Вы не президент(или же другое важное для государства лицо) чтобы удалять страницу конституции")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['viewrage'])
def viewrage(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        constitut = load("constitution.json")
        if message.text[9:]:
            if isnum(message.text[9:]):
                try:
                    bot.reply_to(message, constitut[message.text[9:]]['text'])
                except:
                    bot.reply_to(message, "Такого номера страницы не существует!")
            else:
                yes = ''
                for name, value in constitut.items():
                    if value['name'] == message.text[9:]:
                        yes = name
                        break
                if yes:
                    bot.reply_to(message, constitut[name]['text'])
                else:
                    bot.reply_to(message, "Такой страницы не существует!")
        else:
            bot.reply_to(message, "Аргумент пуст")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['rages'])
def rages(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return

        constitut = load("constitution.json")
        text = f"----- Страницы конституции -----"
        for name, value in constitut.items():
            text += f"{name}. {value['name']}"
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['add'])
def add(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        constitut = load("constitution.json")
        if data['users'][i]['president'] or i == USERY:
            if message.text[9:]:
                args = message.text[9:].split("; ")
                if len(args) != 2:
                    bot.reply_to(message, "Аргументов должно быть 2!")
                    return

                yes = ''
                for name, value in constitut.items():
                    if value['name'] == message.text[9:]:
                        yes = name
                        break
                if yes:
                    bot.reply_to(message, "Имя страницы индентична к другой, придумайте новую имя страницы")
                else:
                    constitut[str(len(constitut.keys()) + 1)] = {
                        'name': args[0],
                        'text': args[1]
                    }
                    save("constitution.json", constitut)
                    bot.reply_to(message, f"Страница создана под номером {len(constitut.keys())}!")
            else:
                bot.reply_to(message, "Аргумент пуст")
        else:
            bot.reply_to(message, "Вы не президент(или же другое важное для государства лицо) чтобы удалять страницу конституции")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

@bot.message_handler(commands=['ibt'])
def ibtfunc(message: types.Message):
    data = load("data.json")
    i = str(message.from_user.id)
    if i in data["users"].keys():
        if data['users'][i]['banned']:
            bot.reply_to(message, "Вы ЗАБАНЕНЫ!")
            return
        
        if message.text[5:]:
            bot.reply_to(message, f"ibt2: {ibt.IBT2(message.text[5:])}")
        else:
            bot.reply_to(message, "Мало текста")
    else:
        bot.reply_to(message, "Зарегистрируйтесь!")

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"An error occurred: {e.__class__.__name__}: {e}")

import math
import re
from decimal import *

import telebot
from telebot import types
import datetime
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot
from telegram import *
from telegram.ext import *
from telegram.utils.request import Request
from datetime import datetime
import requests
from ugc.models import Profile
from ugc.models import Message
from ugc.models import TypeOfRequisites
from ugc.models import Type
from ugc.models import CleanBTC
from ugc.models import QueueToReq
from ugc.models import CleanAccount
from ugc.models import Admin
from ugc.models import Config
from ugc.models import Request
from ugc.models import Transaction
import csv
import requests
from bs4 import BeautifulSoup

flag = 0


def get_info():
    response = requests.get(url="https://yobit.net/api/3/info")

    with open("info.txt", "w") as file:
        file.write(response.text)

    return response.text


def get_btc_to_rub(coin1="BTC", coin2="RUB"):
    key = "https://api.binance.com/api/v3/ticker/price?symbol=BTCRUB"
    data = requests.get(key)
    data = data.json()
    return float(data['price'])


# Инфа о парах за последние 24 часа
def get_ticker(coin1="btc", coin2="usd"):
    response = requests.get(url=f"https://yobit.net/api/3/ticker/{coin1}_{coin2}?ignore_invalid=1")

    with open("ticker.txt", "w") as file:
        file.write(response.text)

    return response.text


# Инфа о выставленных на покупку и продажу ордерах. Возращает общую сумму закупа монет в последниз 150 ордерах(макс 2000)
def get_depth(coin1="btc", coin2="usd", limit=150):
    response = requests.get(url=f"https://yobit.net/api/3/depth/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")

    with open("depth.txt", "w") as file:
        file.write(response.text)

    bids = response.json()[f"{coin1}_{coin2}"]["bids"]

    total_bids_amount = 0
    for item in bids:
        price = item[0]
        coin_amount = item[1]

        total_bids_amount += price * coin_amount

    return f"Total bids: {round(total_bids_amount, 2)} $"


# Инфа о совершонных сделках по покупки и продаже.Возращает общую сумму проданых и купленых монет
def get_trades(coin1="btc", coin2="usd", limit=150):
    response = requests.get(url=f"https://yobit.net/api/3/trades/{coin1}_{coin2}?limit={limit}&ignore_invalid=1")

    with open("trades.txt", "w") as file:
        file.write(response.text)

    total_trade_ask = 0
    total_trade_bid = 0

    for item in response.json()[f"{coin1}_{coin2}"]:
        if item["type"] == "ask":
            total_trade_ask += item["price"] * item["amount"]
        else:
            total_trade_bid += item["price"] * item["amount"]

    info = f"[-] TOTAL {coin1} SELL: {round(total_trade_ask, 2)} $\n[+] TOTAL {coin1} BUY: {round(total_trade_bid, 2)} $"

    return info


def get_data(coin1="btc", coin2="usd"):
    req = requests.get(url=f"https://yobit.net/api/3/ticker/{coin1}_{coin2}?ignore_invalid=1")
    response = req.json()
    sell_price = response[f"{coin1}_{coin2}"]["sell"]
    return f"{datetime.now().strftime('%Y-%m-%d %H:%M')}\nSell BTC price: {round(sell_price, 2)} $"


class Command(BaseCommand):
    help = "Telegram-Bot"
    index = 0
    languages = {
        'ru': {
            'Hi': 'Привет',
            'Hi Bot': 'Это крипто-обменный бот',
            'Select crypto': 'Выберите криптовалюту котрую хотите купить',
            'Wait requisite': 'Пожалуйста, подождите, администратор выдаст Вам реквизит для оплаты, отправляйте строго указанную сумму для быстрого обмена',
            'Enter amount': 'Введите сумму в ₽ на котрую хотите купить \nТекущая стоимость 1 BTC ',
            'Wait request': 'Пожалуйста подождите администратор проверит ваш запрос',
            'Amount': 'Ваша сумма',
            'in btc': 'в BTC',
            'price': 'Курс',
            'help': 'Помощь',
            'buy crypto': 'Купить',
            'total bids': '',
            'total trade': '',
            'send account': 'Пожалуйста, введите адрес своего bitcoin кошелька',
            'reject': 'отклонен',
            'done': 'выполнен',
            'request': 'Запрос',
            'status': 'статус',
            'processed': 'обрабатывается',
            'change': 'Изменить',
            'buy': 'Купить',
            'butStatus': 'Статус',
            'credit card': 'Банковская карта',
            'sim card': 'Сим карта',
            'wallet': 'Кошелек',
            'qiwi': "Qiwi",
            'payment type': 'Пожалуйста выберите способ оплаты',
            'clean crypto': 'Чистка BTC 🪙',
            'clean price': 'Введите сумму которую хотите обменять',
            'send': 'Пожалуйста отправте',
            'to': 'на адрес',
            'confirmed': 'Ваш запрос выполнен',
            'confirm': 'Подтвердить отправку',
            'to credit card': 'на номер карты',
            'to sim card': 'на номер сим карты',
            'to qiwi': 'на qiwi кошелек',
            'commission': 'Комиссии на чистку:\n\nот 0.05 до 0.1  - 5%\nот 0.1 до 0.5 - 4%\nот 0.5 до 2 - 3%\nот 2 - 2%\n\nВведите ваш кошелек для приема чистых BTC.\nРекомендация использовать всегда новый адрес'
        },
        'eng': {
            'qiwi': "Qiwi",
            'Hi': 'Hello',
            'Hi Bot': 'It is a exchange crypto bot',
            'Select crypto': 'Select crypto which you want to buy',
            'Wait requisite': 'Please wait administrator has give you requisites',
            'Enter amount': 'Enter the amount in ₽ \n Current price for 1 BTC is',
            'Wait request': 'Please wait administrator has checking your request',
            'Amount': 'You amount',
            'in btc': 'in BTC',
            'price': 'Price',
            'help': 'Help',
            'buy crypto': 'Buy crypto',
            'send account': 'Please send your btc account',
            'reject': 'reject',
            'done': 'done',
            'request': 'request',
            'status': 'status',
            'processed': 'processed',
            'change': 'Change',
            'buy': 'Buy',
            'butStatus': 'Status',
            'credit card': 'Credit card',
            'sim card': 'Sim card',
            'wallet': 'Wallet',
            'payment type': 'Please set payment type',
        }

    }

    def handle(self, *args, **options):
        bot = telebot.TeleBot(settings.TOKEN)
        self.stdout.write("Bot started")

        def start(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard1.add(types.KeyboardButton(f"{self.languages[p.language]['price']}💲"),
                          types.KeyboardButton(f"{self.languages[p.language]['help']}❓")) \
                .add(types.KeyboardButton(f"{self.languages[p.language]['buy crypto']} 🔄"),
                     types.KeyboardButton(f"{self.languages[p.language]['clean crypto']}"))
            bot.send_message(message.chat.id,
                             text=f"{self.languages[p.language]['Hi']} <b>{message.from_user.first_name}</b>! {self.languages[p.language]['Hi Bot']}",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard1)

        @bot.message_handler(commands=['start'])
        def do_start(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            p.language = "ru"
            p.save()
            start(message)

        @bot.message_handler(commands=['help'])
        def do_help(message):
            bot.send_message(message.chat.id,
                             text=f"List of all commands:\n/price\n/total_bids_amount\n/total_trade_ask_and_bid")

        @bot.message_handler(commands=['price'])
        def price(message):
            bot.send_message(message.chat.id, text=get_data())

        @bot.message_handler(commands=['total_bids_amount'])
        def total_bids(message):
            bot.send_message(message.chat.id, text=get_depth())

        @bot.message_handler(commands=['total_trade_ask_and_bid'])
        def total_trade(message):
            bot.send_message(message.chat.id, text=get_trades())

        @bot.message_handler(commands=['clean'])
        def clean(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
            bot.send_message(message.chat.id,
                             text=f"{self.languages[p.language]['commission']}", reply_markup=keyboard)
            bot.register_next_step_handler(message, cleanAddress)

        def priceToClean(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            try:
                keyboard = types.InlineKeyboardMarkup()
                accounts = CleanAccount.objects.all()
                for i in range(len(accounts)):
                    if accounts[i].used == "No":
                        m = CleanBTC(btcPrice=str(float(message.text)) + "BTC", )
                        m.save()
                        keyboard.row(
                            types.InlineKeyboardButton(text=f"Подтвердить",
                                                       callback_data="clean_confirm"))

                        bot.send_message(chat_id=message.chat.id,
                                         text=f"ID вашей заявки {m.id}\n"
                                              f"сумма {message.text} BTC")
                        mes = bot.send_message(chat_id=message.chat.id,
                                               text=f"Отправте свои BTC на адресс {accounts[i].account} и затем нажмите подтвердить",
                                               reply_markup=keyboard)
                        accounts[i].used = "Yes"
                        accounts[i].save()
                        m.save()
                        break
                    if i == len(accounts) - 1:
                        print(f"Index {i}")
                        bot.send_message(chat_id=message.chat.id,
                                         text=f"На данный момент нет свободных адресов, пожалуйста, обратитесь немного позже")
            except:
                bot.send_message(chat_id=message.chat.id,
                                 text=f"Неверное значение, пожалуйста введите еще раз.")
                bot.register_next_step_handler(message, priceToClean)



        def cleanAddress(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
            getAdress(message)
            bot.send_message(message.chat.id,
                             text=f"{self.languages[p.language]['clean price']}", reply_markup=keyboard)
            bot.register_next_step_handler(message, priceToClean)

        @bot.callback_query_handler(func=lambda call: call.data == "clean_confirm")
        def confirm(call):
            keyboard = types.InlineKeyboardMarkup()
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard.row(
                types.InlineKeyboardButton(text=f"{self.languages[p.language]['butStatus']}",
                                           callback_data="clean_status"))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f"{self.languages[p.language]['Wait request']}",
                                  parse_mode=ParseMode.HTML, reply_markup=keyboard)
            m, _ = CleanBTC.objects.get_or_create(
                message_id=call.message.message_id,
            )
            m.profile = p
            m.account = p.current_account
            m.status = "processed"
            m.save()

        @bot.callback_query_handler(func=lambda call: call.data == "go_home")
        def confirm(call):
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard1.add(types.KeyboardButton(f"{self.languages[p.language]['price']}💲"),
                          types.KeyboardButton(f"{self.languages[p.language]['help']}❓")) \
                .add(types.KeyboardButton(f"{self.languages[p.language]['buy crypto']} 🔄"),
                     types.KeyboardButton(f"{self.languages[p.language]['clean crypto']}"))
            bot.send_message(chat_id=call.message.chat.id,
                             text=f"Вы в главном меню",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard1)

        @bot.message_handler(commands=['buy'])
        def exchange(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            if p.status == "Unlock":
                t = p.last_lime
                time = datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')
                if int(p.request_count) <= 3:
                    if time + timedelta(minutes=30) <= datetime.now():
                        p.request_count = 0
                        p.save()
                    if int(p.request_count) >= 3 and not (time + timedelta(minutes=30) <= datetime.now()):
                        bot.send_message(chat_id=message.chat.id,
                                         text=f"Доступно только 3 запроса в 30 минут",
                                         parse_mode=ParseMode.HTML)
                    else:
                        keyboard = types.InlineKeyboardMarkup()
                        keyboard.add(types.InlineKeyboardButton(text="BTC", callback_data="btc"))
                        keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
                        bot.send_message(chat_id=message.chat.id,
                                         text=f"{self.languages[p.language]['Select crypto']}",
                                         parse_mode=ParseMode.HTML, reply_markup=keyboard)
                else:
                    bot.send_message(chat_id=message.chat.id,
                                     text=f"Доступно только 3 запроса в 30 минут",
                                     parse_mode=ParseMode.HTML)
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text=f"Вы не можете создавать заявки на обмен",
                                 parse_mode=ParseMode.HTML)

        def getAdress(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            p.current_account = message.text
            p.save()

        def getTypeOfRequisites(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )

            getAdress(message)
            keyboard = types.InlineKeyboardMarkup()
            for i in TypeOfRequisites.objects.all():
                if i.active == "On":
                    price = get_btc_to_rub() + (get_btc_to_rub() * (float(i.percent) / 100))
                    keyboard.add(types.InlineKeyboardButton(
                        text=f"{self.languages[p.language][i.typeOfRequisites]} (курс {price} ₽)",
                        callback_data=i.typeOfRequisites))
            keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
            bot.send_message(chat_id=message.chat.id,
                             text=f"{self.languages[p.language]['payment type']}", reply_markup=keyboard)

        @bot.callback_query_handler(
            func=lambda
                    call: call.data == 'credit card' or call.data == 'sim card' or call.data == 'wallet' or call.data == "qiwi")
        def payment_type(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )

            if call.data == "credit card":
                p.payment_type = "credit card"
            if call.data == "sim card":
                p.payment_type = "sim card"
            if call.data == "wallet":
                p.payment_type = "wallet"
            if call.data == "qiwi":
                p.payment_type = "qiwi"
            p.save()
            t = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
            price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"Укажите желаемую сумму  BTC или RUB",reply_markup=keyboard)
            bot.register_next_step_handler(call.message, transaction)

        @bot.callback_query_handler(func=lambda call: call.data == 'rub_to_btc' or call.data == 'btc_to_rub')
        def convert_price(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            t = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
            if call.data == 'rub_to_btc':
                p.currency = "rub"
                price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"{self.languages[p.language]['Enter amount']} {price} ₽",
                                      reply_markup=keyboard)
            else:
                p.currency = "crypto"
                price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      text=f"Введите сумму в BTC котрую хотите купить\nТекущая стоимость 1 BTC {price} ₽",
                                      reply_markup=keyboard)

            bot.register_next_step_handler(call.message, transaction)
            p.save()

        @bot.callback_query_handler(func=lambda call: call.data == 'btc' or call.data == 'change')
        def btc_buy_handler(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
            if call.data == 'change':
                t = TypeOfRequisites.objects.get(
                    typeOfRequisites=p.payment_type,
                )
                price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
                if p.currency == "crypto":
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text=f"Введите сумму в BTC котрую хотите купить\nТекущая стоимость 1 BTC {price} ₽",
                                          reply_markup=keyboard)
                else:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                          text=f"{self.languages[p.language]['Enter amount']} {price} ₽",
                                          reply_markup=keyboard)
                bot.register_next_step_handler(call.message, transaction)
            else:

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"{self.languages[p.language]['send account']}", reply_markup=keyboard)
                bot.register_next_step_handler(call.message, getTypeOfRequisites)

        @bot.callback_query_handler(func=lambda call: call.data == 'buy')
        def buy_request(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            res = re.findall(r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))(\s₽)", call.message.text)
            price = float(res[0][0])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f"{self.languages[p.language]['Wait requisite']}")
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            type = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )
            keyboard = types.InlineKeyboardMarkup()
            file = open("logs.txt", "a", encoding="utf-8")
            file.write(
                f'id: {id}  Sum: {str(price)}₽ BTC: {price / get_btc_to_rub()} BTC with %: {(get_btc_to_rub() + (get_btc_to_rub() * (float(type.percent) / 100)))} rekvizit: {p.payment_type} date: {datetime.now()}\n')
            file.close()
            btcPrice = get_btc_to_rub() + (get_btc_to_rub() * (float(type.percent) / 100))
            for t in Type.objects.all():
                if t.type.typeOfRequisites == p.payment_type:
                    if float(t.currentPrice) + float(price) <= float(t.limit):
                        m = Message(
                            btcPrice=price / btcPrice,
                        )
                        m.save()
                        t.currentPrice = str(float(t.currentPrice) + float(price))
                        t.save()
                        bot.send_message(chat_id=call.message.chat.id,
                                         text=f"ID вашей заявки {m.id}")
                        keyboard.row(
                            types.InlineKeyboardButton(text=f"{self.languages[p.language]['confirm']}",
                                                       callback_data="confirm"))
                        mes = bot.send_message(chat_id=call.message.chat.id,
                                               text=f"{self.languages[p.language]['send']} {price} ₽ {self.languages[p.language][f'to {t.type.typeOfRequisites}']} {t.number}",
                                               reply_markup=keyboard)
                        m.message_id = mes.message_id
                        m.payment_type = p.payment_type
                        m.number_of_payment = t.number
                        m.save()
                        Transaction(
                            message_id=mes.message_id,
                            fiatPrice=price,
                            type=p.payment_type,
                            number=t.number
                        ).save()
                        Request(
                            profile=p,
                            type=p.payment_type,
                            amount=price,
                            time=datetime.now(),
                        ).save()
                        p.last_lime = str(datetime.now())
                        previous = p.request_count
                        p.request_count = int(previous) + 1
                        p.save()
                        for i in Admin.objects.all():
                            bot.send_message(chat_id=i.external_id,
                                             text=f"New request",
                                             parse_mode=ParseMode.HTML)
                        return

            QueueToReq(
                profile=p.external_id,
                fiatPrice=str(price),
                btcPrice=str(price / btcPrice),
                paymentUserType=p.payment_type
            ).save()

        @bot.callback_query_handler(func=lambda call: call.data == "confirm")
        def confirm(call):
            res = re.findall(r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))(\s₽)", call.message.text)
            print(res[0][0])
            price = float(res[0][0])
            keyboard = types.InlineKeyboardMarkup()
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard.row(
                types.InlineKeyboardButton(text=f"{self.languages[p.language]['butStatus']}", callback_data="status"))
            if call.data == "confirm":
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"{self.languages[p.language]['Wait request']}",
                                      parse_mode=ParseMode.HTML, reply_markup=keyboard)
                m = Message.objects.get(
                    message_id=call.message.message_id,
                )
                m.profile = p
                m.fiatPrice = str(price) + " ₽"
                m.account = p.current_account
                m.status = "processed"
                m.save()

        @bot.callback_query_handler(func=lambda call: call.data == "status" or call.data == "clean_status")
        def status(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )

            try:
                if call.data == "status":
                    message = Message.objects.get(
                        profile=p,
                    )
                if call.data == "clean_status":
                    message = CleanBTC.objects.get(
                        profile=p,
                    )
                bot.send_message(chat_id=call.message.chat.id,
                                 text=f"Заявка №{message.id} {self.languages[p.language]['butStatus']}: {self.languages[p.language][message.status]}",
                                 parse_mode=ParseMode.HTML)
            except (Message.MultipleObjectsReturned, CleanBTC.MultipleObjectsReturned) as e:
                if call.data == "status":
                    message = Message.objects.filter(
                        profile=p,
                    )
                if call.data == "clean_status":
                    message = CleanBTC.objects.filter(
                        profile=p,
                    )
                str = ""
                for i in message:
                    str += f"{self.languages[p.language]['request']} №{i.id} {self.languages[p.language]['status']}: {self.languages[p.language][i.status]}\n"
                bot.send_message(chat_id=call.message.chat.id,
                                 text=f"{str}",
                                 parse_mode=ParseMode.HTML)

        def transaction(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            t = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )
            if message.text.find('.') and 0.0001 <= float(message.text) <= 0.15:
                p.currency = "crypto"
            else:
                p.currency = "rub"

            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(
                types.InlineKeyboardButton(text=f"{self.languages[p.language]['change']}", callback_data="change"),
                types.InlineKeyboardButton(text=f"{self.languages[p.language]['buy']}", callback_data="buy"))
            price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
            keyboard.add(types.InlineKeyboardButton(text="На главную", callback_data="go_home"))
            if checkAccess(message):
                for i in TypeOfRequisites.objects.all():
                    if i.typeOfRequisites == p.payment_type:
                        if p.currency == "crypto":
                            enterPrice = message.text
                            cost = float(message.text) * price
                            message.text = cost
                        if float(i.min_amount) <= float(message.text) <= float(i.max_amount):
                            if p.currency == "crypto":
                                bot.send_message(chat_id=message.chat.id,
                                                 text=f"Ваша сумма {enterPrice} BTC это {message.text} ₽",
                                                 parse_mode=ParseMode.HTML, reply_markup=keyboard)
                            else:
                                bot.send_message(chat_id=message.chat.id,
                                                 text=f"{self.languages[p.language]['Amount']} {message.text} ₽  {self.languages[p.language]['in btc']}: {round(Decimal(float(i.min_amount) / price), 7)}",
                                                 parse_mode=ParseMode.HTML, reply_markup=keyboard)
                        else:
                            bot.send_message(chat_id=message.chat.id,
                                             text=f"Неверное значение\nПроверьте верно ли указали сумму.\nМинимальная сумма "
                                                  f"обмен {round(Decimal(float(i.min_amount) / price), 7)} или {i.min_amount} руб.\n"
                                                  f"Максимальная сумма обмена {round(Decimal(float(i.max_amount) / price), 7)} или {i.max_amount} руб.")

                            bot.register_next_step_handler(message, transaction)
            else:
                bot.register_next_step_handler(message, transaction)
            try:
                i = 0
            except:
                bot.send_message(chat_id=message.chat.id,
                                 text="Пожалуйста введите число")
                bot.send_message(chat_id=message.chat.id,
                                 text=f"{self.languages[p.language]['Enter amount']} {price} ₽", reply_markup=keyboard)
                bot.register_next_step_handler(message, transaction)

        def checkAccess(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            for r in Request.objects.all():
                if r.profile == p:
                    if p.payment_type == r.type and float(message.text) == float(r.amount):
                        time = datetime.strptime(r.time, '%Y-%m-%d %H:%M:%S.%f')
                        if time + timedelta(hours=12) <= datetime.now():
                            p.access = "allowed"
                            p.save()
                        else:
                            p.access = "denied"
                            p.save()
                        break
                    else:
                        p.access = "allowed"
                        p.save()
                else:
                    p.access = "allowed"
                    p.save()
            if p.access == "allowed":
                return True
            else:
                bot.send_message(chat_id=message.chat.id,
                                 text=f"В данный момент на эту сумму нельзя создать заявку попробуйте позже или введите другую сумму")
                return False

        @bot.message_handler(content_types=['text'])
        def do_button(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            if p.access is None and p.status is None:
                p.access = "allowed"
                p.status = "Unlock"

            p.payment_type = "credit card"

            if p.last_lime is None and p.request_count is None:
                p.last_lime = datetime.now()
                p.request_count = 0

            p.save()

            t = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )
            price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
            if message.text == f"{self.languages[p.language]['help']}❓":
                bot.send_message(message.chat.id,
                                 text=f"В случае возникновения вопросов или сложностей с обменом, пожалуйста, свяжитесь с нами. Связь с поддержкой -> @suppbitpay")
            if message.text == f"{self.languages[p.language]['price']}💲":
                bot.send_message(message.chat.id, text=f"Актуальный курс: {price} ₽")
            if message.text == f"{self.languages[p.language]['buy crypto']} 🔄":
                exchange(message)
            if message.text == f"{self.languages[p.language]['clean crypto']}":
                clean(message)

        bot.infinity_polling()

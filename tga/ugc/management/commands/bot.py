import re

import telebot
from telebot import types
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
from ugc.models import Requisites
from ugc.models import TypeOfRequisites
from ugc.models import Type
from ugc.models import Admin
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
    r = requests.get("https://www.coingecko.com/en/coins/bitcoin/rub")
    soup = BeautifulSoup(r.content, "html.parser")

    res = soup.findAll("span", class_="no-wrap")
    return float(res[0].text[1:].replace(',', ''))


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
    languages = {
        'ru': {
            'Hi': 'Привет',
            'Hi Bot': 'Это крипто-обменный бот',
            'Select crypto': 'Выберите криптовалюту котрую хотите купить',
            'Wait requisite': 'Пожалуйста подождите администратор даст вам реквизиты для оплаты, отправляйте строго указанную сумму для быстрого обмена',
            'Enter amount': 'Введите сумму в ₽ на котрую хотите купить \nТекущяя стоимость 1 BTC ',
            'Wait request': 'Пожалуйста подождите администратор проверит ваш запрос',
            'Amount': 'Ваша сумма',
            'in btc': 'в BTC',
            'price': 'Цена',
            'help': 'Помощь',
            'buy crypto': 'Купить',
            'total bids': '',
            'total trade': '',
            'send account': 'Пожалуйста введите адресс своего bitcoin кошелька',
            'reject': 'отклонен',
            'done': 'выполнен',
            'request': 'запрос',
            'status': 'статус',
            'processed': 'обрабатывается',
            'change': 'Изменить',
            'buy': 'Купить',
            'butStatus': 'Статус',
            'credit card': 'Банковская карта',
            'sim card': 'Сим карта',
            'wallet': 'Кошелек',
            'payment type': 'Пожалуйста выберите способ оплаты'
        },
        'eng': {
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

        def setLanguage(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard1.add(types.KeyboardButton(f"{self.languages[p.language]['price']}💲"),
                          types.KeyboardButton(f"{self.languages[p.language]['help']}❓")) \
                .add(types.KeyboardButton(f"{self.languages[p.language]['buy crypto']} 🔄"))
            bot.send_message(message.chat.id,
                             text=f"{self.languages[p.language]['Hi']} <b>{message.from_user.first_name}</b>! {self.languages[p.language]['Hi Bot']}",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard1)

        @bot.message_handler(commands=['start'])
        def do_start(message):
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(types.KeyboardButton('🇷🇺'), types.KeyboardButton('🇺🇸'))
            bot.send_message(message.chat.id,
                             text=f"Please set a language",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard)

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

        @bot.message_handler(commands=['buy'])
        def exchange(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="BTC", callback_data="btc"))
            bot.send_message(chat_id=message.chat.id,
                             text=f"{self.languages[p.language]['Select crypto']}",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard)

        def getAdress(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            p.current_account = message.text
            p.save()
            keyboard = types.InlineKeyboardMarkup()
            for i in TypeOfRequisites.objects.all():
                if i.active == "On":
                    keyboard.add(types.InlineKeyboardButton(text=f"{self.languages[p.language][i.typeOfRequisites]}",
                                                            callback_data=i.typeOfRequisites))
            bot.send_message(chat_id=message.chat.id,
                             text=f"{self.languages[p.language]['payment type']}", reply_markup=keyboard)

        @bot.callback_query_handler(
            func=lambda call: call.data == 'credit card' or call.data == 'sim card' or call.data == 'wallet')
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
            p.save()
            t = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )
            price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
            bot.send_message(chat_id=call.message.chat.id,
                             text=f"{self.languages[p.language]['Enter amount']} {price} ₽")
            bot.register_next_step_handler(call.message, transaction)

        @bot.callback_query_handler(func=lambda call: call.data == 'btc' or call.data == 'change')
        def btc_buy_handler(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )

            if call.data == 'change':
                t = TypeOfRequisites.objects.get(
                    typeOfRequisites=p.payment_type,
                )
                price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"{self.languages[p.language]['Enter amount']} {price} ₽")
                bot.register_next_step_handler(call.message, transaction)
            else:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                      text=f"{self.languages[p.language]['send account']}")
                bot.register_next_step_handler(call.message, getAdress)

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
            t = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )

            file = open("logs.txt", "a")
            file.write(f"id: {id}  сума обміну: {str(price)}₽ BTC: {get_btc_to_rub()} BTC разом з %: {(get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100)))} реквізити: {p.payment_type} дата: {datetime.now()}\n")
            file.close()

            Requisites(
                profile=p,
                paymentUserType=p.payment_type,
                btcPrice=price / (get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))),
                fiatPrice=str(price) + " ₽",
            ).save()

            for i in Admin.objects.all():
                bot.send_message(chat_id=i.external_id,
                                 text=f"New request",
                                 parse_mode=ParseMode.HTML)

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
                bot.send_message(chat_id=call.message.chat.id,
                                 text=f"{self.languages[p.language]['Wait request']}",
                                 parse_mode=ParseMode.HTML, reply_markup=keyboard)
                m, _ = Message.objects.get_or_create(
                    message_id=call.message.message_id,
                )
                m.profile = p
                m.fiatPrice = str(price) + " ₽"
                m.account = p.current_account
                m.status = "processed"
                m.save()

        @bot.callback_query_handler(func=lambda call: call.data == "status")
        def confirm(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )

            try:
                message = Message.objects.get(
                    profile=p,
                )
                bot.send_message(chat_id=call.message.chat.id,
                                 text=f"{self.languages[p.language]['butStatus']}: {self.languages[p.language][message.status]}",
                                 parse_mode=ParseMode.HTML)

            except Message.MultipleObjectsReturned:
                message = Message.objects.filter(
                    profile=p,
                )
                str = ""
                for i in range(len(message)):
                    str += f"{i + 1} {self.languages[p.language]['request']} {self.languages[p.language]['status']}: {self.languages[p.language][message[i].status]}\n"
                bot.send_message(chat_id=call.message.chat.id,
                                 text=f"{str}",
                                 parse_mode=ParseMode.HTML)

        def transaction(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(
                types.InlineKeyboardButton(text=f"{self.languages[p.language]['change']}", callback_data="change"),
                types.InlineKeyboardButton(text=f"{self.languages[p.language]['buy']}", callback_data="buy"))
            t = TypeOfRequisites.objects.get(
                typeOfRequisites=p.payment_type,
            )
            price = get_btc_to_rub() + (get_btc_to_rub() * (float(t.percent) / 100))
            try:
                bot.send_message(chat_id=message.chat.id,
                             text=f"{self.languages[p.language]['Amount']} {message.text} ₽  {self.languages[p.language]['in btc']}: {float(message.text) / price}",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard)
            except:
                bot.send_message(chat_id=message.chat.id,
                                      text="Пожалуйста введите число")
                bot.send_message(chat_id=message.chat.id,
                                      text=f"{self.languages[p.language]['Enter amount']} {price} ₽")
                bot.register_next_step_handler(message, transaction)

        @bot.message_handler(content_types=['text'])
        def do_button(message):
            id = message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
            )
            if message.text == "🇷🇺":
                p.language = "ru"
                p.payment_type = "credit card"
                p.save()
                setLanguage(message)
            if message.text == "🇺🇸":
                p.language = "eng"
                p.payment_type = "credit card"
                p.save()
                setLanguage(message)
            if message.text == f"{self.languages[p.language]['help']}❓":
                bot.send_message(message.chat.id,
                                 text=f"Если возникли вопросы обращайтесь к @suppbitpay")
            if message.text == f"{self.languages[p.language]['price']}💲":
                bot.send_message(message.chat.id, text=f"{get_btc_to_rub()} ₽")
            if message.text == f"{self.languages[p.language]['buy crypto']} 🔄":
                exchange(message)

        bot.infinity_polling()

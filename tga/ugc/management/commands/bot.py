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
import requests
from bs4 import BeautifulSoup


flag = 0


def get_info():
    response = requests.get(url="https://yobit.net/api/3/info")

    with open("info.txt", "w") as file:
        file.write(response.text)

    return response.text


def get_btc_to_rub(coin1="BTC", coin2="RUB"):
    r = requests.get(f"https://freecurrencyrates.com/en/convert-{coin1}-{coin2}")
    soup = BeautifulSoup(r.content, "html.parser")
    res = soup.find(id="value_to")
    return float(res['value'])


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

    def handle(self, *args, **options):
        bot = telebot.TeleBot(settings.TOKEN)
        self.stdout.write("Bot started")


        @bot.message_handler(commands=['start'])
        def do_start(message):
            keyboard1 = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

            keyboard1.add(types.KeyboardButton('Price💲'), types.KeyboardButton('Help❓')) \
                .add(types.KeyboardButton("Total bids"), types.KeyboardButton('Total trade ™'),
                     types.KeyboardButton("Buy crypto 🔄"))
            id = message.chat.id
            text = message.text
            p, _ = Profile.objects.get_or_create(
                external_id=id,
                defaults={
                    'name': message.from_user.username,
                }
            )
            bot.send_message(message.chat.id,
                             text=f"Hello <b>{message.from_user.first_name}</b>! It is a exchange crypto bot",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard1)

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
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text="BTC", callback_data="btc"))
            bot.send_message(chat_id=message.chat.id,
                             text=f"Select crypto which you want to buy",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard)

        @bot.callback_query_handler(func=lambda call: call.data == 'btc' or call.data == 'change')
        def btc_buy_handler(call):
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f"Enter the amount in ₽ \n"
                                       f"Current price for 1 BTC is {get_btc_to_rub()} ₽")
            bot.register_next_step_handler(call.message, transaction)

        @bot.callback_query_handler(func=lambda call: call.data == 'buy')
        def buy_request(call):
            res = re.findall(r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))(\s₽)", call.message.text)
            price = float(res[0][0])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                                  text=f"Please wait administrator has give you requisites")
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
                defaults={
                    'name': call.message.from_user.username,
                }
            )
            Requisites(
                profile=p,
                btcPrice=price / get_btc_to_rub(),
                fiatPrice=str(price) + " ₽",
            ).save()

        @bot.callback_query_handler(func=lambda call: call.data == "confirm")
        def confirm(call):
            res = re.findall(r"([+-]?([0-9]+([.][0-9]*)?|[.][0-9]+))(\s₽)", call.message.text)
            print(res[0][0])
            price = float(res[0][0])
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(types.InlineKeyboardButton(text="Status", callback_data="status"))
            if call.data == "confirm":
                bot.send_message(chat_id=call.message.chat.id,
                                 text="Please wait administrator has checking your request",
                                 parse_mode=ParseMode.HTML, reply_markup=keyboard)
                id = call.message.chat.id
                p, _ = Profile.objects.get_or_create(
                    external_id=id,
                    defaults={
                        'name': call.message.from_user.username,
                    }
                )
                Message(
                    profile=p,
                    btcPrice=price / get_btc_to_rub(),
                    fiatPrice=str(price) + " ₽",
                    status="send"
                ).save()

        @bot.callback_query_handler(func=lambda call: call.data == "status")
        def confirm(call):
            id = call.message.chat.id
            p, _ = Profile.objects.get_or_create(
                external_id=id,
                defaults={
                    'name': call.message.from_user.username,
                }
            )

            try:
                message = Message.objects.get(
                    profile=p,
                )
                bot.send_message(chat_id=call.message.chat.id,
                                 text=f"Status: {message.status}",
                                 parse_mode=ParseMode.HTML)

            except Message.MultipleObjectsReturned:
                message = Message.objects.filter(
                    profile=p,
                )
                str = ""
                for i in range(len(message)):
                    str += f"{i + 1} request status: {message[i].status}\n"
                bot.send_message(chat_id=call.message.chat.id,
                                 text=f"{str}",
                                 parse_mode=ParseMode.HTML)

        def transaction(message):
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(types.InlineKeyboardButton(text="Change", callback_data="change"),
                         types.InlineKeyboardButton(text="Buy", callback_data="buy"))
            price = float(message.text)
            bot.send_message(chat_id=message.chat.id,
                             text=f"You amount {message.text} ₽  in BTC: {float(message.text) / get_btc_to_rub()}",
                             parse_mode=ParseMode.HTML, reply_markup=keyboard)

        @bot.message_handler(content_types=['text'])
        def do_button(message):
            if message.text == "Help❓":
                bot.send_message(message.chat.id,
                                 text=f"List of all commands:\n/price\n/total_bids_amount\n/total_trade_ask_and_bid")
            if message.text == "Price💲":
                bot.send_message(message.chat.id, text=f"{get_btc_to_rub()} ₽")
            if message.text == "Total bids":
                bot.send_message(message.chat.id, text=get_depth())
            if message.text == "Total trade ™":
                bot.send_message(message.chat.id, text=get_trades())
            if message.text == "Buy crypto 🔄":
                exchange(message)

        bot.infinity_polling()

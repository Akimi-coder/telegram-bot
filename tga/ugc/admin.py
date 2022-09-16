from django.contrib import admin

# Register your models here.
from django.forms import TextInput, Textarea
from django.db import models
from .forms import AdminForm
from .forms import ProfileForm
from .forms import TypeFrom
from .forms import TypeOfRequisitesForm
from .models import Profile
from .models import Message
from .models import CleanAccount
from .models import TypeOfRequisites
from .models import Type
from .models import CleanBTC
from .models import Admin
from .models import Config
from .models import Request
from .models import QueueToReq
import telebot
from django.conf import settings
from telebot import types
from django.db.models import F
import requests
from bs4 import BeautifulSoup
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
import datetime
from datetime import datetime, timedelta


def get_btc_to_rub(coin1="BTC", coin2="RUB"):
    r = requests.get("https://www.coingecko.com/en/coins/bitcoin/rub")
    soup = BeautifulSoup(r.content, "html.parser")

    res = soup.findAll("span", class_="no-wrap")
    return float(res[0].text[1:].replace(',', ''))


languages = {
    'ru': {
        'send': 'Пожалуйста отправте',
        'to': 'на адрес',
        'confirmed': 'Ваш запрос выполнен',
        'reject': 'Ваш запрос отклонен',
        'confirm': 'Подтвердить отправку',
        'credit card': 'на номер карты',
        'sim card': 'на номер сим карты',
        'qiwi': 'на qiwi кошелек',
    },
    'eng': {
        'send': 'Please send',
        'confirmed': 'Your request is confirmed',
        'reject': 'Your request is reject',
        'confirm': 'Confirm',
        'credit card': 'to credit card',
        'sim card': 'to sim card',
        'qiwi': 'to qiwi',
    }
}


@admin.action(description='Confirmed')
def confirmed_request(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    import random
    code_length = 10

    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

    code = ""
    chekcher = False
    while True:
        for index in range(code_length):
            code = code + random.choice(characters)

        for i in Message.objects.all():
            if i.present == code:
                chekcher = False
                break
            else:
                chekcher = True

        if (chekcher):
            break
    for obj in queryset:
        payment = Type.objects.get(
            number=obj.number_of_payment,
        )
        payment.currentPrice = str(float(payment.currentPrice) + float(obj.fiatPrice[:obj.fiatPrice.index(' ')]))
        payment.save()
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"{languages[obj.profile.language]['confirmed']}")
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"Код для участия в  конкурсе {code}")
    queryset.update(status="done", present=code)


@admin.action(description='Confirmed')
def confirmed_clean_request(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    import random
    code_length = 10

    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ123456789"

    code = ""
    chekcher = False
    while (True):
        for index in range(code_length):
            code = code + random.choice(characters)

        for i in CleanBTC.objects.all():
            if (i.present == code):
                chekcher = False
                break
            else:
                chekcher = True

        if (chekcher):
            break
    for obj in queryset:
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"{languages[obj.profile.language]['confirmed']}")
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"Код для участия в  конкурсе {code}")
    queryset.update(status="done", present=code)


@admin.action(description='Requisites')
def requisites(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    keyboard = types.InlineKeyboardMarkup()
    for obj in queryset:
        m = Message(
            btcPrice=obj.btcPrice,
        )
        m.save()
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"ID вашей заявки {m.id}")
        keyboard.row(
            types.InlineKeyboardButton(text=f"{languages[obj.profile.language]['confirm']}", callback_data="confirm"))
        mes = bot.send_message(chat_id=obj.profile.external_id,
                               text=f"{languages[obj.profile.language]['send']} {obj.fiatPrice} {languages[obj.profile.language][obj.type.type.typeOfRequisites]} {obj.type.number}",
                               reply_markup=keyboard)
        m.message_id = mes.message_id
        m.payment_type = obj.paymentUserType
        m.save()
    queryset.delete()


@admin.action(description='Reject')
def reject_request(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    for obj in queryset:
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"{languages[obj.profile.language]['reject']}")
    queryset.update(status="reject")


@admin.register(TypeOfRequisites)
class TypeOfRequisitesAdmin(admin.ModelAdmin):
    list_display = ('typeOfRequisites', 'percent', 'active', 'min_amount', 'max_amount')
    list_editable = ('active',)
    form = TypeOfRequisitesForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 0, 'cols': 0})},
    }
    list_editable = ('percent', 'active', 'min_amount', 'max_amount')


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        bot = telebot.TeleBot(settings.TOKEN)
        keyboard = types.InlineKeyboardMarkup()
        profiles = QueueToReq.objects.filter(paymentUserType=obj.type.typeOfRequisites)
        price = 0
        for i in profiles:
            price += float(i.fiatPrice)
            if price <= float(obj.limit):
                p, _ = Profile.objects.get_or_create(
                    external_id=i.profile,
                )
                m = Message(
                    btcPrice=price / get_btc_to_rub(),
                )
                m.save()
                bot.send_message(chat_id=i.profile,
                                 text=f"ID вашей заявки {m.id}")
                keyboard.row(
                    types.InlineKeyboardButton(text=f"{languages[p.language]['confirm']}",
                                               callback_data="confirm"))
                mes = bot.send_message(chat_id=p.external_id,
                                       text=f"{languages[p.language]['send']} {i.fiatPrice} ₽ {languages[p.language][f'{obj.type.typeOfRequisites}']} {obj.number}",
                                       reply_markup=keyboard)
                m.message_id = mes.message_id
                m.payment_type = p.payment_type
                m.number_of_payment = obj.number
                m.save()
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
                                     text=f"New request")
                instance = QueueToReq.objects.get(profile=i.profile, paymentUserType=i.paymentUserType,
                                                  fiatPrice=i.fiatPrice)
                instance.delete()
        super().save_model(request, obj, form, change)

    list_display = ('id', 'type', 'number', 'currentPrice', 'limit')
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 0, 'cols': 0})},
    }
    list_editable = ('limit', 'currentPrice')

    form = TypeFrom


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', "external_id", "current_account", "language", "payment_type", "last_lime", "request_count", "status",
        "access",'currency')
    list_editable = ('status',)
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'message_id', 'profile', 'btcPrice', 'fiatPrice', 'account', 'status', 'payment_type',
        'number_of_payment', 'present',
        'created_at')
    actions = [confirmed_request, reject_request]
    list_filter = (('created_at', DateRangeFilter), ('created_at', DateTimeRangeFilter), "created_at")


@admin.register(Admin)
class ProfAdmin(admin.ModelAdmin):
    list_display = ('id', "external_id", "name")
    form = AdminForm


@admin.register(Request)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', "type", "amount", 'time')


@admin.register(CleanBTC)
class CleanBTCAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'message_id', 'profile', 'btcPrice', 'account', 'status', 'present',
        'created_at')
    actions = [confirmed_clean_request, reject_request]
    list_filter = (('created_at', DateRangeFilter), ('created_at', DateTimeRangeFilter), "created_at")


@admin.register(QueueToReq)
class QueueToReqAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', "paymentUserType", "fiatPrice")


@admin.register(CleanAccount)
class CleanAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'account')

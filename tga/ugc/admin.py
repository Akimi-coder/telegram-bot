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
from .models import TypeOfRequisites
from .models import Type
from .models import Requisites
from .models import Admin
from .models import Config
from .models import Request
import telebot
from django.conf import settings
from telebot import types
from django.db.models import F
import requests
from bs4 import BeautifulSoup


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
        'wallet': 'на кошелек',
    },
    'eng': {
        'send': 'Please send',
        'confirmed': 'Your request is confirmed',
        'reject': 'Your request is reject',
        'confirm': 'Confirm',
        'credit card': 'to credit card',
        'sim card': 'to sim card',
        'wallet': 'to wallet',
    }
}


@admin.action(description='Confirmed')
def confirmed_request(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    for obj in queryset:
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"{languages[obj.profile.language]['confirmed']}")
    queryset.update(status="done")


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
    list_display = ('typeOfRequisites', 'percent', 'active')
    list_editable = ('active',)
    form = TypeOfRequisitesForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 0, 'cols': 0})},
    }
    list_editable = ('percent','active')


@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'number')
    form = TypeFrom


@admin.register(Requisites)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'paymentUserType', 'profile', 'btcPrice', 'fiatPrice', 'type', 'created_at')
    list_editable = ('type',)

    actions = [requisites]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', "external_id", "current_account", "language", "payment_type", "last_lime", "request_count","status","access")
    list_editable = ('status',)
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message_id', 'profile', 'btcPrice', 'fiatPrice', 'account', 'status', 'created_at')
    actions = [confirmed_request, reject_request]


@admin.register(Admin)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', "external_id", "name")
    form = AdminForm


@admin.register(Config)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'min_amount',)
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 0, 'cols': 0})},
    }
    list_editable = ('min_amount',)


@admin.register(Request)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile',"type","amount",'time')

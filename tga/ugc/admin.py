from django.contrib import admin

# Register your models here.

from .forms import ProfileForm
from .forms import TypeFrom
from .forms import TypeOfRequisitesForm
from .models import Profile
from .models import Message
from .models import TypeOfRequisites
from .models import Type
from .models import Requisites
import telebot
from django.conf import settings
from telebot import types
from django.db.models import F

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
        sum = float(obj.fiatPrice[0:obj.fiatPrice.find('₽')])
        percent = sum * (float(obj.type.percent) / 100)

        keyboard.row(
            types.InlineKeyboardButton(text=f"{languages[obj.profile.language]['confirm']}", callback_data="confirm"))
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"{languages[obj.profile.language]['send']} {sum + percent} ₽ {languages[obj.profile.language][obj.type.type.typeOfRequisites]} {obj.type.number}",
                         reply_markup=keyboard)
    queryset.delete()


@admin.action(description='Reject')
def reject_request(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    for obj in queryset:
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"{languages[obj.profile.language]['reject']}")
    queryset.update(status="reject")


@admin.register(TypeOfRequisites)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('typeOfRequisites','active')
    list_editable = ('active',)
    form = TypeOfRequisitesForm


@admin.register(Type)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'number', 'percent')
    form = TypeFrom


@admin.register(Requisites)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'paymentUserType', 'profile', 'btcPrice', 'fiatPrice', 'type', 'created_at')
    list_editable = ('type',)
    actions = [requisites]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', "external_id", "current_account", "language", "payment_type")
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'btcPrice', 'fiatPrice', 'account', 'status', 'created_at')
    actions = [confirmed_request, reject_request]

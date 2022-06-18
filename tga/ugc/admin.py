from django.contrib import admin

# Register your models here.

from .forms import ProfileForm
from .forms import TypeForm
from .models import Profile
from .models import Message
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
        'Credit card': 'на номер карты',
        'Sim card': 'на номер сим карты',
        'Wallet': 'на кошелек',
    },
    'eng': {
        'send': 'Please send',
        'confirmed': 'Your request is confirmed',
        'reject': 'Your request is reject',
        'confirm': 'Confirm',
        'Credit card': 'to credit card',
        'Sim card': 'to sim card',
        'Wallet': 'to wallet',
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
        keyboard.row(
            types.InlineKeyboardButton(text=f"{languages[obj.profile.language]['confirm']}", callback_data="confirm"))
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"{languages[obj.profile.language]['send']} {obj.fiatPrice} {languages[obj.profile.language][obj.type.typeOfRequisites]} {obj.type.number}",
                         reply_markup=keyboard)
    queryset.delete()


@admin.action(description='Reject')
def reject_request(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    for obj in queryset:
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"")
    queryset.update(status="reject")


@admin.register(Type)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'typeOfRequisites', 'number')
    form = TypeForm


@admin.register(Requisites)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'paymentUserType', 'profile', 'btcPrice', 'fiatPrice', 'type', 'created_at')
    list_editable = ('type',)
    actions = [requisites]



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', "external_id", "name", "current_account", "language","payment_type")
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'btcPrice', 'fiatPrice', 'account', 'status', 'created_at')
    actions = [confirmed_request, reject_request]

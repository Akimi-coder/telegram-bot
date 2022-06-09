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


@admin.action(description='Confirmed')
def confirmed_request(modeladmin, request, queryset):
    queryset.update(status="done")


@admin.action(description='Requisites')
def requisites(modeladmin, request, queryset):
    bot = telebot.TeleBot(settings.TOKEN)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton(text="Confirm", callback_data="confirm"))
    for obj in queryset:
        bot.send_message(chat_id=obj.profile.external_id,
                         text=f"Please send {obj.fiatPrice} to {obj.type.number}",reply_markup=keyboard)
    queryset.delete()


@admin.action(description='Reject')
def reject_request(modeladmin, request, queryset):
    queryset.update(status="reject")


@admin.register(Type)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'typeOfRequisites', 'number')
    form = TypeForm


@admin.register(Requisites)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'profile', 'btcPrice', 'fiatPrice', 'created_at')
    list_editable = ('type',)
    actions = [requisites]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', "external_id", "name", "current_account")
    form = ProfileForm


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'btcPrice', 'fiatPrice', 'account', 'status', 'created_at')
    actions = [confirmed_request, reject_request]

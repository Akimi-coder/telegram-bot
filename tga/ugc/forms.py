from django import forms
from .models import Profile
from .models import Type
from .models import TypeOfRequisites
from .models import Admin
import datetime as d


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'external_id',
        )


class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = (
            'external_id',
            'name',
        )
        widgets = {
            'external_id': forms.TextInput,
            'name': forms.TextInput,
        }


class TypeFrom(forms.ModelForm):
    class Meta:
        model = Type
        fields = (
            'type',
            'number',
            'limit'
        )
        widgets = {
            'number': forms.TextInput,
            'limit': forms.TextInput,
        }


class TypeOfRequisitesForm(forms.ModelForm):
    class Meta:
        model = TypeOfRequisites
        fields = (
            'typeOfRequisites',
            'active'
        )
        widgets = {
            'typeOfRequisites': forms.TextInput,
            'active': forms.Select(choices=TypeOfRequisites.CHOICES)
        }

from django import forms
from .models import Profile
from .models import Type


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'external_id',
            'name',
        )
        widgets = {
            'name': forms.TextInput,
        }


class TypeForm(forms.ModelForm):
    class Meta:
        model = Type
        fields = (
            'typeOfRequisites',
            'number',
        )
        widgets = {
            'typeOfRequisites': forms.TextInput,
            'number': forms.TextInput,
        }

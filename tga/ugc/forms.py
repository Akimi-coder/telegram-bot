from django import forms
from .models import Profile
from .models import Type
from .models import TypeOfRequisites


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = (
            'external_id',
        )


class TypeFrom(forms.ModelForm):
    class Meta:
        model = Type
        fields = (
            'type',
            'number',
            'percent',
        )
        widgets = {
            'number': forms.TextInput,
            'percent': forms.TextInput,
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
        }

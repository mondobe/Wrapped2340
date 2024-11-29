from django.forms import forms, CharField, HiddenInput


class CreateDuoWrappedForm(forms.Form):
    invite_token = CharField(max_length=16, widget=HiddenInput())
    timeframe = CharField(widget=HiddenInput())
    public = CharField()

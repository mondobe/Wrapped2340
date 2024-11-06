from django.forms import forms, CharField, HiddenInput


class WhatsTheBuzzForm(forms.Form):
    chosen_artist = CharField(widget=HiddenInput())
    correct_hash = CharField(widget=HiddenInput())

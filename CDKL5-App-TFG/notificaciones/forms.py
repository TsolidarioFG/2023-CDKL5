from django import forms
from notificaciones import models
from notificaciones import constants

class newNoticeForm(forms.Form):
    titulo = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Título*'}), label='')
    texto = forms.CharField(max_length=400, required=True, widget=forms.Textarea(attrs={'placeholder': '¿Qué ha ocurrido?', 'rows': '5'}), label='')
    adjunto = forms.FileField(required=False, label='Documento Adjunto:')
    destino = forms.ChoiceField(choices=constants.NoticeScope.choices, label='Destinatarios:*')
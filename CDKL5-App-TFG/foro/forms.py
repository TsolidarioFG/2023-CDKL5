from django import forms

class newEntryForm(forms.Form):
    titulo = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Título del Post*'}))
    texto = forms.CharField(max_length=400, required=True, widget=forms.Textarea(attrs={'placeholder': 'Escriba sus ideas para compartir aquí!', 'rows': '5'}))

class responseForm (forms.Form):
    texto = forms.CharField(max_length=400, required=True, widget=forms.Textarea(attrs={'placeholder': 'Escriba sus ideas para compartir aquí!', 'rows': '5'}))
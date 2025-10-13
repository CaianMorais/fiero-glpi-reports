from django import forms
from datetime import date

STATUS_CHOICES = [
    ("6", "Fechado"),
    ("1", "Novo"),
    ("2", "Atribuído"),
    ("3", "Planejado"),
    ("4", "Pendente"),
]

class FiltroConsulta(forms.Form):

    inicio = forms.DateField(
        label='Início',
        initial=date.today().replace(day=1),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )

    fim = forms.DateField(
        label='Fim',
        initial=date.today(),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )
    status = forms.ChoiceField(
        label="Status",
        choices=STATUS_CHOICES,
        required=True
    )
from django import forms
from datetime import date

STATUS_CHOICES = [
    ("6", "Fechado"),
    ("1", "Novo"),
    ("2", "Atribuído"),
    ("3", "Planejado"),
    ("4", "Pendente"),
]

class ChamadosPorArea(forms.Form):

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

AREA_CHOICES = [
    ('', 'Selecione o departamento'),
    ('FIERO > TI', 'Coordenação de Tecnologia da Informação'),
    ('FIERO > CEBEP', 'CEBEP'),
    ('FIERO > COMPRAS', 'Coordenação de Compras'),
    ('FIERO > CONTABILIDADE', 'Supervisão Contábil'),
    ('FIERO > CPL', 'Compras e Licitação'),
    ('FIERO > FINANCEIRO', 'Coordenação Financeira'),
    ('FIERO > INFRA', 'Supervisão de Logística e Infraestrutura'),
    ('FIERO > MERCADO', 'Mercado'),
]

class MediaSatisfacao(forms.Form):
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

    area = forms.ChoiceField(
        label="Área",
        choices=AREA_CHOICES,
        required=True
    )
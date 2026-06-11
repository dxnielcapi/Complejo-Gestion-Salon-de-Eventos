import re
from datetime import date
from django import forms
from venues.models import Espacio, Paquete, ServicioAdicional


TIPO_EVENTO_CHOICES = [
    ('boda', 'Boda'),
    ('xv_anos', 'XV años'),
    ('bautizo', 'Bautizo'),
    ('aniversario', 'Aniversario'),
    ('empresarial', 'Empresarial'),
    ('cumpleanos', 'Cumpleaños'),
]


class Paso1Form(forms.Form):
    tipo_evento = forms.ChoiceField(choices=TIPO_EVENTO_CHOICES, widget=forms.RadioSelect)
    num_invitados = forms.IntegerField(min_value=1, max_value=600)
    hora_inicio = forms.TimeField(widget=forms.Select(choices=[
        ('14:00', '14:00'), ('15:00', '15:00'), ('16:00', '16:00'),
        ('17:00', '17:00'), ('18:00', '18:00'), ('19:00', '19:00'),
        ('20:00', '20:00'),
    ]))


class Paso2Form(forms.Form):
    espacio_id = forms.IntegerField(widget=forms.HiddenInput)


class Paso3Form(forms.Form):
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class Paso4Form(forms.Form):
    paquete_id = forms.IntegerField(widget=forms.HiddenInput)


class Paso5Form(forms.Form):
    servicios = forms.ModelMultipleChoiceField(
        queryset=ServicioAdicional.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )


class Paso6Form(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellidos = forms.CharField(max_length=100)
    email = forms.EmailField()
    telefono = forms.CharField(max_length=20)


class Paso7Form(forms.Form):
    nombre_titular = forms.CharField(
        max_length=100,
        label='Nombre del titular',
        widget=forms.TextInput(attrs={'placeholder': 'Como aparece en la tarjeta', 'autocomplete': 'cc-name'}),
    )
    numero_tarjeta = forms.CharField(
        max_length=16,
        min_length=16,
        label='Número de tarjeta',
        widget=forms.TextInput(attrs={'placeholder': '1234567890123456', 'maxlength': '16', 'inputmode': 'numeric', 'autocomplete': 'cc-number'}),
    )
    fecha_vencimiento = forms.CharField(
        max_length=5,
        label='Vencimiento (MM/AA)',
        widget=forms.TextInput(attrs={'placeholder': 'MM/AA', 'maxlength': '5', 'inputmode': 'numeric', 'autocomplete': 'cc-exp'}),
    )
    cvv = forms.CharField(
        max_length=3,
        min_length=3,
        label='CVV',
        widget=forms.PasswordInput(attrs={'placeholder': '•••', 'maxlength': '3', 'inputmode': 'numeric', 'autocomplete': 'cc-csc'}),
    )
    aceptar_terminos = forms.BooleanField(required=True, label='Acepto los términos y condiciones')

    def clean_nombre_titular(self):
        value = self.cleaned_data['nombre_titular'].strip()
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value):
            raise forms.ValidationError('Solo se permiten letras y espacios, sin caracteres especiales.')
        return value.upper()

    def clean_numero_tarjeta(self):
        value = self.cleaned_data['numero_tarjeta'].replace(' ', '')
        if not re.match(r'^\d{16}$', value):
            raise forms.ValidationError('El número debe tener exactamente 16 dígitos numéricos.')
        return value

    def clean_fecha_vencimiento(self):
        value = self.cleaned_data['fecha_vencimiento'].strip()
        if not re.match(r'^\d{2}/\d{2}$', value):
            raise forms.ValidationError('Formato inválido. Usa MM/AA (ejemplo: 08/27).')
        mes, anno = value.split('/')
        mes_int = int(mes)
        anno_int = int(anno) + 2000
        if mes_int < 1 or mes_int > 12:
            raise forms.ValidationError('El mes debe estar entre 01 y 12.')
        hoy = date.today()
        if anno_int < hoy.year or (anno_int == hoy.year and mes_int < hoy.month):
            raise forms.ValidationError('La tarjeta está vencida.')
        return value

    def clean_cvv(self):
        value = self.cleaned_data['cvv']
        if not re.match(r'^\d{3}$', value):
            raise forms.ValidationError('El CVV debe tener exactamente 3 dígitos numéricos.')
        return value


class LiquidacionForm(forms.Form):
    nombre_titular = forms.CharField(
        max_length=100,
        label='Nombre del titular',
        widget=forms.TextInput(attrs={'placeholder': 'Como aparece en la tarjeta', 'autocomplete': 'cc-name'}),
    )
    numero_tarjeta = forms.CharField(
        max_length=16,
        min_length=16,
        label='Número de tarjeta',
        widget=forms.TextInput(attrs={'placeholder': '1234567890123456', 'maxlength': '16', 'inputmode': 'numeric', 'autocomplete': 'cc-number'}),
    )
    fecha_vencimiento = forms.CharField(
        max_length=5,
        label='Vencimiento (MM/AA)',
        widget=forms.TextInput(attrs={'placeholder': 'MM/AA', 'maxlength': '5', 'inputmode': 'numeric', 'autocomplete': 'cc-exp'}),
    )
    cvv = forms.CharField(
        max_length=3,
        min_length=3,
        label='CVV',
        widget=forms.PasswordInput(attrs={'placeholder': '•••', 'maxlength': '3', 'inputmode': 'numeric', 'autocomplete': 'cc-csc'}),
    )
    confirmar_pago = forms.BooleanField(required=True, label='Confirmo el pago del saldo restante')

    def clean_nombre_titular(self):
        value = self.cleaned_data['nombre_titular'].strip()
        if not re.match(r'^[a-zA-ZÀ-ÿ\s]+$', value):
            raise forms.ValidationError('Solo se permiten letras y espacios, sin caracteres especiales.')
        return value.upper()

    def clean_numero_tarjeta(self):
        value = self.cleaned_data['numero_tarjeta'].replace(' ', '')
        if not re.match(r'^\d{16}$', value):
            raise forms.ValidationError('El número debe tener exactamente 16 dígitos numéricos.')
        return value

    def clean_fecha_vencimiento(self):
        value = self.cleaned_data['fecha_vencimiento'].strip()
        if not re.match(r'^\d{2}/\d{2}$', value):
            raise forms.ValidationError('Formato inválido. Usa MM/AA (ejemplo: 08/27).')
        mes, anno = value.split('/')
        mes_int = int(mes)
        anno_int = int(anno) + 2000
        if mes_int < 1 or mes_int > 12:
            raise forms.ValidationError('El mes debe estar entre 01 y 12.')
        hoy = date.today()
        if anno_int < hoy.year or (anno_int == hoy.year and mes_int < hoy.month):
            raise forms.ValidationError('La tarjeta está vencida.')
        return value

    def clean_cvv(self):
        value = self.cleaned_data['cvv']
        if not re.match(r'^\d{3}$', value):
            raise forms.ValidationError('El CVV debe tener exactamente 3 dígitos numéricos.')
        return value

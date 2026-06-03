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
    aceptar_terminos = forms.BooleanField(required=True, label='Acepto los términos y condiciones')

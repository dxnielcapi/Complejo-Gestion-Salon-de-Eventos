from django import forms


class LoginForm(forms.Form):
    username = forms.EmailField(label='Correo electrónico', widget=forms.EmailInput(
        attrs={'placeholder': 'tu@correo.com', 'autocomplete': 'email'}
    ))
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput(
        attrs={'placeholder': '••••••••'}
    ))

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label=_("Пароль"))
    password_confirm = forms.CharField(widget=forms.PasswordInput, label=_("Подтвердите пароль"))

    class Meta:
        model = User
        fields = ['username']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise ValidationError(_("Пароли не совпадают"))
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

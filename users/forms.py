# users/forms.py - VERSIÓN SEGURA
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
from django.conf import settings

# OBTENER EL MODELO DE USUARIO - ESTA ES LA CLAVE
User = get_user_model()


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contrasenya"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirma la contrasenya"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        """Validación simplificada para evitar errores de Djongo"""
        email = self.cleaned_data.get('email')

        # SOLUCIÓN: Validación básica sin .exists() para desarrollo
        if settings.DEBUG:
            # En desarrollo, solo validar formato
            if not email or '@' not in email:
                raise ValidationError("Si us plau, introdueix un email vàlid.")
            return email

        # En producción, intentar verificación
        try:
            # Método alternativo para evitar problemas con Djongo
            count = User.objects.filter(email=email).count()
            if count > 0:
                raise ValidationError("Aquest email ja està registrat.")
        except Exception:
            # Si falla, solo validar formato
            if not email or '@' not in email:
                raise ValidationError("Si us plau, introdueix un email vàlid.")

        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Les contrasenyes no coincideixen.")

        if password1 and len(password1) < 8:
            raise ValidationError("La contrasenya ha de tenir almenys 8 caràcters.")

        if password1 and not re.search(r'[A-Z]', password1):
            raise ValidationError("La contrasenya ha de tenir almenys una majúscula.")

        if password1 and not re.search(r'\d', password1):
            raise ValidationError("La contrasenya ha de tenir almenys un número.")

        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomUserUpdateForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        required=False,
        label="Biografia"
    )
    avatar = forms.FileField(
        required=False,
        label="Avatar",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuari o Email",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Contrasenya",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        username_or_email = self.cleaned_data.get('username')

        # Intentar encontrar por email
        try:
            user = User.objects.get(email=username_or_email)
            self.cleaned_data['username'] = user.username
        except (User.DoesNotExist, AttributeError):
            # No es un email válido, continuar con username
            pass
        except Exception:
            # Cualquier otro error, ignorar
            pass

        return super().clean()
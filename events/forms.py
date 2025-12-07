from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_datetime
from .models import Event

User = get_user_model()


class EventCreationForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DDTHH:MM',
                'pattern': '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}',
                'title': 'Format 24h obligatori: YYYY-MM-DDTHH:MM (ex: 2025-12-04T18:30)'
            },
            format='%Y-%m-%dT%H:%M'  # ← FORMATO 24H FIJO
        ),
        label="Data i hora programada",
        input_formats=['%Y-%m-%dT%H:%M'],  # ← SOLO ESTE FORMATO
        help_text="<strong>Format 24h obligatori:</strong> YYYY-MM-DDTHH:MM<br>Exemple: 2025-12-04T18:30"
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date',
                  'thumbnail', 'max_viewers', 'tags', 'stream_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Títol de l\'esdeveniment'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripció detallada...'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'max_viewers': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 1000}),
            'tags': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'etiqueta1, etiqueta2, etiqueta3...'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
        labels = {
            'title': 'Títol',
            'description': 'Descripció',
            'category': 'Categoria',
            'scheduled_date': 'Data i hora',
            'thumbnail': 'Imatge de portada',
            'max_viewers': 'Màxim espectadors',
            'tags': 'Etiquetes',
            'stream_url': 'URL del streaming',
        }

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')

        # ELIMINAR: No permitir limpieza de AM/PM
        # Si llega con AM/PM, es porque el frontend lo envió mal
        if scheduled_date and isinstance(scheduled_date, str):
            if 'AM' in scheduled_date.upper() or 'PM' in scheduled_date.upper():
                raise forms.ValidationError(
                    "Format 24h obligatori. Utilitza: YYYY-MM-DDTHH:MM (ex: 2025-12-04T18:30)"
                )

        if scheduled_date and scheduled_date < timezone.now():
            raise forms.ValidationError("La data programada no pot ser en el passat.")

        return scheduled_date

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data.get('max_viewers')
        if max_viewers and (max_viewers < 1 or max_viewers > 1000):
            raise forms.ValidationError("El màxim d'espectadors ha d'estar entre 1 i 1000.")
        return max_viewers


class EventUpdateForm(forms.ModelForm):
    scheduled_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DDTHH:MM',
                'pattern': '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}',
                'title': 'Format 24h obligatori: YYYY-MM-DDTHH:MM'
            },
            format='%Y-%m-%dT%H:%M'  # ← MISMO FORMATO 24H
        ),
        label="Data i hora programada",
        input_formats=['%Y-%m-%dT%H:%M'],  # ← SOLO ESTE FORMATO
        help_text="Format 24h: YYYY-MM-DDTHH:MM"
    )

    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date',
                  'thumbnail', 'max_viewers', 'tags', 'status', 'stream_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'max_viewers': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 1000}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.status == 'live':
            self.fields['scheduled_date'].disabled = True

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')

        # Rechazar AM/PM
        if scheduled_date and isinstance(scheduled_date, str):
            if 'AM' in scheduled_date.upper() or 'PM' in scheduled_date.upper():
                raise forms.ValidationError("Format 24h obligatori. Elimina AM/PM.")

        if self.instance.status == 'live' and scheduled_date != self.instance.scheduled_date:
            raise forms.ValidationError("No es pot canviar la data d'un esdeveniment en directe.")

        return scheduled_date

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if self.user and self.instance.creator != self.user:
            raise forms.ValidationError("Només el creador pot canviar l'estat de l'esdeveniment.")
        return status


class EventSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cercar esdeveniments...'
        }),
        label="Cercar"
    )

    category = forms.ChoiceField(
        required=False,
        choices=[('', 'Totes les categories')] + list(Event.CATEGORY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Categoria"
    )

    status = forms.ChoiceField(
        required=False,
        choices=[('', 'Tots els estats')] + list(Event.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Estat"
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Des de"
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Fins a"
    )
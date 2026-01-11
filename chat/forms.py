from django import forms
from .models import ChatMessage

BAD_WORDS = ['puta', 'mierda', 'idiota']


class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Escriu un missatge...',
                'maxlength': 500
            })
        }

    def clean_message(self):
        message = self.cleaned_data['message'].strip()

        if not message:
            raise forms.ValidationError("El missatge no pot estar buit")

        for word in BAD_WORDS:
            if word in message.lower():
                raise forms.ValidationError("Llenguatge ofensiu detectat")

        return message

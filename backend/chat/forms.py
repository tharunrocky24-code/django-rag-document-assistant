from django import forms
from documents.models import Document

class ChatQueryForm(forms.Form):
    question = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'chat-input',
            'class': 'chat-input',
            'placeholder': 'Ask any question about your documents...',
            'autocomplete': 'off'
        }),
        max_length=2000
    )
    conversation_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )
    document_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput()
    )

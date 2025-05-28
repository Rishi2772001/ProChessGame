from django import forms
from django.core import validators
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import chess 

def validate_chess_position(value):
    if len(value) != 2 or not (value[0] in "abcdefgh") or not (value[1] in "12345678"):
        raise forms.ValidationError("Enter a valid chessboard position (e.g., 'e2').")

class MoveForm(forms.Form):
    move = forms.CharField(
        max_length=5,
        label='Move',
        help_text='Enter your move in UCI format, e.g., e2e4',
        widget=forms.TextInput(attrs={'placeholder': 'e2e4'})
    )

    def clean_move(self):
        move_input = self.cleaned_data['move'].strip().lower()
        if len(move_input) < 4 or len(move_input) > 5:
            raise forms.ValidationError('Invalid move format. Please enter a move like e2e4.')
        return move_input

class JoinForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'size': '30'}), help_text="Enter a valid email address.")

    class Meta:
        model = get_user_model()  # Using the correct user model
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'password1': "Enter a strong password.",
            'password2': "Enter the same password as before, for verification."
        }

    def __init__(self, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())



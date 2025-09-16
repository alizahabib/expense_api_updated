from django import forms
from .models import CustomUser


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    

from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'title', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'placeholder': 'yyyy-mm-dd',  # 👈 Placeholder text
                }
            ),
        }
        
        
        
#new

    
from django import forms
from .models import Team, CustomUser

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'members']
        widgets = {
            'members': forms.CheckboxSelectMultiple(attrs={
                'style': 'max-height: 200px; overflow-y: auto; list-style: none;'
            })
        }
        
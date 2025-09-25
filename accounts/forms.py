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

"""
from django import forms
from .models import Team, CustomUser

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'members', 'team_lead']
        widgets = {
            'members': forms.CheckboxSelectMultiple(attrs={
                'style': 'max-height: 200px; overflow-y: auto; list-style: none;',
            }),
        }
"""

from django import forms
from .models import Team, CustomUser

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'members', 'team_lead']
        widgets = {
            'members': forms.CheckboxSelectMultiple(attrs={
                'style': 'max-height: 200px; overflow-y: auto; list-style: none;',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get all user IDs who are already assigned to any team
        assigned_user_ids = Team.objects.values_list('members__id', flat=True).distinct()

        # Filter out users who are already in a team
        self.fields['members'].queryset = CustomUser.objects.exclude(id__in=assigned_user_ids)
        self.fields['team_lead'].queryset = CustomUser.objects.exclude(id__in=assigned_user_ids)

from django import forms
from accounts.models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'title', 'amount', 'date', 'receipt', 'notes']
        widgets = {
           'date': forms.DateInput(attrs={'type': 'date'}, format='%d-%m-%y')
        }

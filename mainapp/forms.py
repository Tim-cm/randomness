from django import forms
from .models import Income, Expense

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['campus', 'income_group', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
        }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['campus', 'description', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
        }
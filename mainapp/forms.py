from django import forms
from .models import Income, Expense, Campus

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

class ReportForm(forms.Form):
    campus = forms.ModelChoiceField(queryset=Campus.objects.all())
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date must be on or before end date.")
        return cleaned_data
    

from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import IncomeForm, ExpenseForm
from .models import Campus, Income, Expense

def dashboard(request):
    if request.method == 'POST':
        form_name = request.POST.get('form_name')

        if form_name == 'income':
            income_form = IncomeForm(request.POST)
            if income_form.is_valid():
                income = income_form.save()
                income.apply_split_rules()
                messages.success(request, f"Income of {income.amount} added and split for {income.campus}.")
            else:
                messages.error(request, "Could not add income. Check the form.")
            return redirect('dashboard')


        elif form_name == 'expense':
                    expense_form = ExpenseForm(request.POST)
                    if expense_form.is_valid():
                        expense = expense_form.save()
                        messages.success(request, f"Expense of {expense.amount} added  for {expense.campus}.")
                    else:
                        messages.error(request, "Could not add expense. Check the form.")
                    return redirect('dashboard')

    context = {
         'income_form': IncomeForm(), 
         'expense_form': ExpenseForm(),
         'campus': Campus.objects.all(),
         'recent_incomes': Income.objects.select_related('campus').order_by('-id')[:10],
         'recent_expenses': Expense.objects.select_related('campus').order_by('-id')[:10]
    }
    return render(request, 'mainapp/dashboard.html', context)
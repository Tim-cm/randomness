from django.shortcuts import render, redirect
from django.contrib import messages

from .forms import IncomeForm, ExpenseForm, ReportForm
from .models import Campus, Income, Expense

from django.http import HttpResponse
from .reports import generate_report

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

def _run_report_from_get(request):
    """Shared by both the on-screen report and the .txt download.
    Returns (form, report_dict_or_None)."""
    form = ReportForm(request.GET or None)
    report = None
    if request.GET and form.is_valid():
         report = generate_report(
              campus=form.cleaned_data['campus'],
              start_date=form.cleaned_data['start_date'],
              end_date=form.cleaned_data['end_date'],
         )
    return form, report

def report(request):
     form, report_data = _run_report_from_get(request)
     return render(request, 'mainapp/report.html', {'form': form, 'report': report_data, 'query_string': request.GET.urlencode()})

def report_download(request):
     form, report_data = _run_report_from_get(request)
     if report_data is None:
          return redirect('report')

     lines = [
          f"Report for: {report_data['campus']}",
          f"Period: {report_data['start_date']} to {report_data['end_date']}",
          ""
          f"Total income: {report_data['total_income']}",
          f"Local total: {report_data['local_total']}",
          f"Overall total: {report_data['overall_total']}",
          f"Ckc total: {report_data['ckc_total']}",
          f"Total expenses: {report_data['total_expenses']}",
          f"Opening balance: {report_data['opening_balance']}",    
          f"Closing balance: {report_data['closing_balance']}",         
     ]
     content = "\n".join(lines)

     response = HttpResponse(content, content_type='text/plain')
     filename = f"report_{report_data['campus'].name}_{report_data['start_date']}_{report_data['end_date']}.txt"
     response['Content-Disposition'] = f'attachment; filename="{filename}"'
     return response

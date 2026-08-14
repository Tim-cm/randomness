from decimal import Decimal
from django.db.models import Sum

from .models import Income, IncomeAllocation, Expense


def generate_report(campus, start_date, end_date):
    """Compute the full report for one campus over [start_date, end_date],
    both dates inclusive. Every query below is filtered by `campus`
    (directly or via income__campus) so no other campus' data
    can leak in.
    """

    zero = Decimal('0.00')
    total_income = Income.objects.filter(campus=campus, date__range=(start_date, end_date)).aggregate(t=Sum('amount'))['t'] or zero
    total_expenses = Expense.objects.filter(campus=campus, date__range=(start_date, end_date)).aggregate(t=Sum('amount'))['t'] or zero

    def subgroup_total(subgroup, date_lt=None, date_range=None):
        qs = IncomeAllocation.objects.filter(income__campus=campus, subgroup=subgroup)
        if date_range is not None:
            qs = qs.filter(income__date__range=date_range)
        if date_lt is not None:
            qs = qs.filter(income__date__lt=date_lt)
        return qs.aggregate(t=Sum('amount'))['t'] or zero

    local_income_in_range = subgroup_total('local', date_range=(start_date, end_date))
    overall_total = subgroup_total('overall', date_range=(start_date, end_date))
    ckc_total = subgroup_total('ckc', date_range=(start_date, end_date))

    local_total = local_income_in_range - total_expenses

    prior_local = subgroup_total('local', date_lt=start_date)
    prior_expenses = Expense.objects.filter(campus=campus, date__lt=start_date).aggregate(t=Sum('amount'))['t'] or zero
    opening_balance = prior_local - prior_expenses
    closing_balance = opening_balance + local_total

    return{
        'campus': campus,
        'start_date': start_date,
        'end_date': end_date,
        'total_income': total_income,
        'local_total': local_total,
        'overall_total': overall_total,
        'ckc_total': ckc_total,
        'total_expenses': total_expenses,
        'opening_balance': opening_balance,
        'closing_balance': closing_balance,
    }
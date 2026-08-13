from django.contrib import admin
from .models import Campus, SplitRule, Income, IncomeAllocation, Expense

admin.site.register(Campus)
admin.site.register(SplitRule)
admin.site.register(Income)
admin.site.register(IncomeAllocation)
admin.site.register(Expense)
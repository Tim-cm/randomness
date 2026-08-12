from django.db import models
from django.db.models import Sum
from decimal import Decimal


class Campus(models.Model):
    """One of the 5 campuses. Everything else in the app
    (income, expenses, reports) is scoped to one campus.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SplitRule(models.Model):
    """Predetermined % of each income group that goes to each sub-group.
    Global — shared by every organization. Expect exactly 3 rows per
    income group (local + overall + CKC), summing to 100%.""" 
    class IncomeGroup(models.TextChoices):
       TITHE = 'TITHE', 'Group TITHE'
       COMBINED_OFFERING = 'COMBINED_OFFERING', 'Group COMBINED_OFFERING'
       LCB_OFFERING = 'LCB_OFFERING', 'Group LCB_OFFERING'
       LOOSE_OFFERING = 'LOOSE_OFFERING', 'Group LOOSE_OFFERING'

    class SubGroup(models.TextChoices):
       LOCAL ='local', 'local'
       OVERALL ='overall', 'overall'
       CKC ='ckc', 'ckc'

    income_group = models.CharField(max_length=20, choices=IncomeGroup.choices)
    subgroup = models.CharField(max_length=10, choices=SubGroup.choices)
    percent = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['income_group', 'subgroup'],
                name='unique_group_subgroup_rule',
            )
        ]

    def __str__(self):
        return f"{self.get_income_group_display()} -> {self.get_subgroup_display()} ({self.percent}%)"

    @classmethod
    def percent_total_for_group(cls, income_group):
        """Sum of percentages currently defined for one income group.
        Should equal 100.00 once you've entered all 3 rows for that group."""
        total = cls.objects.filter(income_group=income_group).aggregate(t=Sum('percent'))['t']
        return total or Decimal('0.00')
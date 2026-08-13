from django.db import models
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP


class Campus(models.Model):
    """One of the 5 campuses. Everything else in the app
    (income, expenses, reports) is scoped to one campus.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SplitRule(models.Model):
    """Predetermined % of each income group that goes to each sub-group.
    Global — shared by every campus. Expect exactly 3 rows per
    income group (local + overall + ckc), summing to 100%.""" 
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

class Income(models.Model):
    """One income entry for one campus, in one of the 4 campuses
    (TITHE/COMBINED_OFFERING/LCB_OFFERING/LOOSE_OFFERING). Split into IncomeAllocation rows (local/overall/ckc)
    once apply_split_rules() is called."""

    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='incomes')
    income_group = models.CharField(max_length=20, choices=SplitRule.IncomeGroup.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.campus} - {self.get_income_group_display()}: {self.amount}"

    def apply_split_rules(self):
        """(Re)compute this income's local/overall/ckc allocations from
        the current SplitRule rows for its income_group. Safe to call
        more than once — old allocations are cleared first."""
        self.allocations.all().delete()
        rules = SplitRule.objects.filter(income_group=self.income_group)
        for rule in rules:
            split_amount = (self.amount * rule.percent / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            IncomeAllocation.objects.create(income=self, subgroup=rule.subgroup, amount=split_amount)

class IncomeAllocation(models.Model):
    """One computed slice of an Income (e.g. the 'local' portion).
    A snapshot, not a live link to SplitRule — editing a rule later
    won't retroactively change past allocations."""

    income = models.ForeignKey(Income, on_delete=models.CASCADE, related_name='allocations')
    subgroup = models.CharField(max_length=10, choices=SplitRule.SubGroup.choices)
    amount =models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.income} -> {self.get_subgroup_display()}: {self.amount}"

class Expense(models.Model):
    """One expense entry for one campus.The
    report step later subtracts these from that campuse's income
    local_total only."""
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.campus} - {self.amount} ({self.date})"


    
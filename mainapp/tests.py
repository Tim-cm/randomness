from django.test import TestCase
from django.db import IntegrityError
from .models import Campus, SplitRule, Income, Expense

from decimal import Decimal


class CampusModelTests(TestCase):
    def test_campus_created_with_name(self):
        camp = Campus.objects.create(name="Camp A")
        self.assertEqual(camp.name, "Camp A")
        self.assertEqual(str(camp), "Camp A")

    def test_two_campuses_are_indipendent(self):
        camp_a = Campus.objects.create(name="Camp A")
        camp_b = Campus.objects.create(name="Camp B")
        self.assertNotEqual(camp_a.pk, camp_b.pk)
        self.assertEqual(Campus.objects.count(), 2)

    def test_campus_name_must_be_unique(self):
        Campus.objects.create(name="Camp A")
        with self.assertRaises(IntegrityError):
            Campus.objects.create(name="Camp A")


class SplitRuleModelTests(TestCase):
    def test_percent_total_sums_correctly(self):
        SplitRule.objects.create(income_group='TITHE', subgroup='local', percent=Decimal('50.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='overall', percent=Decimal('30.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='ckc', percent=Decimal('20.00'))  
        self.assertEqual(SplitRule.percent_total_for_group('TITHE'), Decimal('100.00'))  

    def test_percent_total_for_group_with_no_rules_is_zero(self):
        self.assertEqual(SplitRule.percent_total_for_group('COMBINED_OFFERING'), Decimal('0.00')) 

    def test_duplicate_group_subgroup_pair_rejected(self):
        SplitRule.objects.create(income_group='LCB_OFFERING', subgroup='local', percent=Decimal('10.00'))  
        with self.assertRaises(IntegrityError):
            SplitRule.objects.create(income_group='LCB_OFFERING', subgroup='local', percent=Decimal('50.00')) 



class IncomeSplitTests(TestCase):
    def setUp(self):
        self.camp = Campus.objects.create(name="Camp A")
        #TITHE
        SplitRule.objects.create(income_group='TITHE', subgroup='local', percent=Decimal('50.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='overall', percent=Decimal('25.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='ckc', percent=Decimal('25.00'))          
        # COMBINED_OFFERING
        SplitRule.objects.create(income_group='COMBINED_OFFERING', subgroup='local', percent=Decimal('20.00'))
        SplitRule.objects.create(income_group='COMBINED_OFFERING', subgroup='overall', percent=Decimal('0.00'))
        SplitRule.objects.create(income_group='COMBINED_OFFERING', subgroup='ckc', percent=Decimal('80.00'))                        
        # LCB_OFFERING
        SplitRule.objects.create(income_group='LCB_OFFERING', subgroup='local', percent=Decimal('10.00'))
        SplitRule.objects.create(income_group='LCB_OFFERING', subgroup='overall', percent=Decimal('10.00'))
        SplitRule.objects.create(income_group='LCB_OFFERING', subgroup='ckc', percent=Decimal('80.00'))                        
        # LOOSE_OFFERING     
        SplitRule.objects.create(income_group='LOOSE_OFFERING', subgroup='local', percent=Decimal('100.00'))
        SplitRule.objects.create(income_group='LOOSE_OFFERING', subgroup='overall', percent=Decimal('0.00'))
        SplitRule.objects.create(income_group='LOOSE_OFFERING', subgroup='ckc', percent=Decimal('0.00'))   

    def _allocation_dict(self, income):
        income.apply_split_rules()                      
        return {a.subgroup: a.amount for a in income.allocations.all()}

    def test_group_a_split(self):
        income = Income.objects.create(campus=self.camp, income_group='TITHE', amount=Decimal('5000.00'))
        result = self._allocation_dict(income)
        self.assertEqual(result['local'], Decimal('2500.00'))
        self.assertEqual(result['overall'], Decimal('1250.00'))
        self.assertEqual(result['ckc'], Decimal('1250.00'))

    def test_group_b_split(self):
        income = Income.objects.create(campus=self.camp, income_group='COMBINED_OFFERING', amount=Decimal('4000.00'))
        result = self._allocation_dict(income)
        self.assertEqual(result['local'], Decimal('800.00'))
        self.assertEqual(result['overall'], Decimal('0.00'))
        self.assertEqual(result['ckc'], Decimal('3200.00'))

    def test_group_c_split(self):
        income = Income.objects.create(campus=self.camp, income_group='LCB_OFFERING', amount=Decimal('1000.00'))
        result = self._allocation_dict(income)
        self.assertEqual(result['local'], Decimal('100.00'))
        self.assertEqual(result['overall'], Decimal('100.00'))
        self.assertEqual(result['ckc'], Decimal('800.00'))

    def test_group_d_split(self):
        income = Income.objects.create(campus=self.camp, income_group='LOOSE_OFFERING', amount=Decimal('750.00'))
        result = self._allocation_dict(income)
        self.assertEqual(result['local'], Decimal('750.00'))
        self.assertEqual(result['overall'], Decimal('0.00'))
        self.assertEqual(result['ckc'], Decimal('0.00'))                

    def test_reapplying_split_does_not_duplicate(self):
        income = Income.objects.create(campus=self.camp, income_group='TITHE', amount=Decimal('5000.00'))
        income.apply_split_rules()
        income.apply_split_rules()
        self.assertEqual(income.allocations.count(), 3)

class ExpenseModelTests(TestCase):
    def test_expense_created_for_campus(self):
        camp = Campus.objects.create(name="camp A")
        expense = Expense.objects.create(campus=camp, amount=Decimal('300.00'), description="Food")
        self.assertEqual(expense.campus, camp)
        self.assertEqual(expense.amount, Decimal('300.00'))

    def test_expenses_are_campus_specfic(self):
        camp_a = Campus.objects.create(name="Camp A")
        camp_b = Campus.objects.create(name="Camp B")
        Expense.objects.create(campus=camp_a, amount=Decimal('100.00'))
        Expense.objects.create(campus=camp_b, amount=Decimal('50.00'))
        Expense.objects.create(campus=camp_b, amount=Decimal('25.00'))

        self.assertEqual(camp_a.expenses.count(), 1)
        self.assertEqual(camp_b.expenses.count(), 2)
        self.assertEqual(camp_a.expenses.first().amount, Decimal('100.00'))

    def test_deleting_campus_deletes_its_expenses(self):
        camp = Campus.objects.create(name="Camp A")
        Expense.objects.create(campus=camp, amount=Decimal('100.00'))
        camp.delete()
        self.assertEqual(Expense.objects.count(), 0)
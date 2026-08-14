from django.test import TestCase, Client
from django.db import IntegrityError
from .models import Campus, SplitRule, Income, Expense

from decimal import Decimal

from datetime import date, timedelta
from .reports import generate_report


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

class ReportTests(TestCase):
    def setUp(self):
        self.camp_a = Campus.objects.create(name='Camp A')
        self.camp_b = Campus.objects.create(name='Camp B')
        SplitRule.objects.create(income_group='TITHE', subgroup='local', percent=Decimal('50.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='overall', percent=Decimal('25.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='ckc', percent=Decimal('25.00'))

    def _income(self, camp, amount, on_date):
        income = Income.objects.create(campus=camp, income_group='TITHE', amount=Decimal(amount))
        income.apply_split_rules()
        Income.objects.filter(pk=income.pk).update(date=on_date)
        return income

    def test_report_excludes_other_campus_data(self):
        self._income(self.camp_a, '1000.00', date(2026, 1, 10))
        self._income(self.camp_b, '5000.00', date(2026, 1, 10))
        Expense.objects.filter

        report = generate_report(self.camp_a, date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(report['total_income'], Decimal('1000.00'))

    def test_date_range_boundaries_are_inclusive_and_exclusive_correctly(self):
        self._income(self.camp_a, '100.00', date(2026, 1, 1)) # exactly on start
        self._income(self.camp_a, '200.00', date(2026, 1, 31)) # exactly on end
        self._income(self.camp_a, '300.00', date(2025, 12, 31)) # one day before start
        self._income(self.camp_a, '400.00', date(2026, 2, 1)) # one day after end

        report = generate_report(self.camp_a, date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(report['total_income'], Decimal('300.00'))

    def test_expenses_reduce_local_total_only(self):
        self._income(self.camp_a, '1000.00', date(2026, 1, 10))

        expense = Expense.objects.create(campus=self.camp_a, amount=Decimal('100.00'))
        Expense.objects.filter(pk=expense.pk).update(date=date(2026, 1, 15))

        report = generate_report(self.camp_a, date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(report['local_total'], Decimal('400.00'))
        self.assertEqual(report['overall_total'], Decimal('250.00'))
        self.assertEqual(report['ckc_total'], Decimal('250.00'))

    def test_opening_balance_reflects_only_this_campus_prior_history(self):
        #Camp A history before the report range
        self._income(self.camp_a, '1000.00', date(2025, 12, 1))
        old_expense = Expense.objects.create(campus=self.camp_a, amount=Decimal('50.00'))
        Expense.objects.filter(pk=old_expense.pk).update(date=date(2025, 12, 5))

        report_before = generate_report(self.camp_a, date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(report_before['opening_balance'], Decimal('450.00'))

        # On addition of camp B's activity in the same prior period camp B's opening balance does not change
        self._income(self.camp_b, '9000.00', date(2025, 12, 1))
        Expense.objects.create(campus=self.camp_b, amount=Decimal('999.00'))

        report_after = generate_report(self.camp_a, date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(report_after['opening_balance'], Decimal('450.00'))

    def test_closing_balance_equals_opening_plus_local_total(self):
        self._income(self.camp_a, '1000.00', date(2025, 12, 1))
        self._income(self.camp_a, '2000.00', date(2026, 1, 10))

        report = generate_report(self.camp_a, date(2026, 1, 1), date(2026, 1, 31))
        self.assertEqual(report['opening_balance'], Decimal('500.00'))
        self.assertEqual(report['local_total'], Decimal('1000.00'))
        self.assertEqual(report['closing_balance'], Decimal('1500.00'))


class DashboardViewtests(TestCase):
    def setUp(self):
        self.client = Client()
        self.camp = Campus.objects.create(name="Camp A")
        SplitRule.objects.create(income_group='TITHE', subgroup='local', percent=Decimal('50.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='overall', percent=Decimal('30.00'))
        SplitRule.objects.create(income_group='TITHE', subgroup='ckc', percent=Decimal('20.00'))

    def test_dashboard_get_returns_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_posting_income_creates_income_and_allocations(self):
        response = self.client.post('/', {
            'form_name': 'income',
            'campus': self.camp.pk,
            'income_group': 'TITHE',
            'amount': '1000.00',
        })
        self.assertEqual(response.status_code, 302) # redirected back to dashboard
        income = Income.objects.get(campus=self.camp)
        self.assertEqual(income.amount, Decimal('1000.00'))
        self.assertEqual(income.allocations.count(), 3)
        local = income.allocations.get(subgroup='local')
        self.assertEqual(local.amount, Decimal('500.00'))

    def test_posting_expense_creates_expense(self):
        response = self.client.post('/', {
            'form_name': 'expense',
            'campus': self.camp.pk,
            'description': 'P.A',
            'amount': '250.00',
        })
        self.assertEqual(response.status_code, 302)
        expense = Expense.objects.get(campus=self.camp)
        self.assertEqual(expense.amount, Decimal('250.00'))

    def test_posting_invalid_income_does_not_crash_or_save(self):
        response =self.client.post('/', {
            'form_name': 'income',
            'campus': self.camp.pk,
            'income_group': 'TITHE',
            'amount': '' # missing required amount
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Income.objects.count(), 0)
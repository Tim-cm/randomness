from django.test import TestCase
from django.db import IntegrityError
from .models import Campus, SplitRule

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
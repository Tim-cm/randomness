from django.test import TestCase
from django.db import IntegrityError
from .models import Campus

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

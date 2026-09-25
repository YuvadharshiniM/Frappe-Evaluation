# # Copyright (c) 2026, Yuvadharshini M and Contributors
# # See license.txt

# # import frappe
# from frappe.tests import IntegrationTestCase


# # On IntegrationTestCase, the doctype test records and all
# # link-field test record dependencies are recursively loaded
# # Use these module variables to add/remove to/from that list
# EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
# IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]

# class IntegrationTestJobCard(IntegrationTestCase):
# 	"""
# 	Integration tests for JobCard.
# 	Use this class for testing interactions between multiple components.
# 	"""

# 	pass


import frappe

from frappe.tests.utils import FrappeTestCase


def make_device_type(**kwargs):
    data = {
        "doctype": "Device Type",
    }

    data.update(kwargs)

    return frappe.get_doc(data).insert()


def make_technician(**kwargs):
    data = {
        "doctype": "Technician",
        "status": "Active",
        "specialization": "Laptop",
    }

    data.update(kwargs)

    return frappe.get_doc(data).insert()


def make_spare_part(stock=10, **kwargs):
    data = {
        "doctype": "Spare Part",
        "stock": stock,
    }

    data.update(kwargs)

    return frappe.get_doc(data).insert()


def make_job_card(submit=False, **kwargs):
    data = {
        "doctype": "Job Card",
        "device_type": ...,
        "assigned_technician": ...,
        "status": ...,
    }

    data.update(kwargs)

    job_card = frappe.get_doc(data).insert()

    if submit:
        job_card.submit()

    return job_card


class TestJobCard(FrappeTestCase):

    def setUp(self):
        super().setUp()

        # FrappeTestCase automatically rolls back the database transaction after each test,
        # so explicit cleanup of documents created during individual tests is usually unnecessary.
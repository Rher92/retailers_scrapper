"""
Celery config file

https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

"""
from __future__ import absolute_import
import time
import os
import logging
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger

from django.conf import settings


# this code copied from manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retailers_scrapper.settings')

app = Celery("retailers_scrapper")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from santaclara_base.models import Icon

class Command(BaseCommand):
    help = 'Add icon'

    def handle(self, *args, **options):
        for html in args:
            icon,created=Icon.objects.get_or_create(html=html)
            if created:
                print "Created icon "+html

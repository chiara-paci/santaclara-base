#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from santaclara_base.models import Version

class Command(BaseCommand):
    help = 'Rebuild cache'

    def handle(self, *args, **options):
        for version in Version.objects.all():
            label=version.created.strftime("%Y%m%d.%H%M%S.%f")
            version.label=label
            version.save()

#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from santaclara_base.models import Version,VersionedAbstract

class Command(BaseCommand):
    help = 'Rebuild cache'

    def handle(self, *args, **options):
        version=Version.objects.get(id=0)
        version.is_current=True
        version.save()
        ctypes=set()
        for version in Version.objects.all():
            ctypes.add(version.content_type)
        models=filter(lambda m: issubclass(m,VersionedAbstract),map(lambda x: x.model_class(),list(ctypes)))
        for m in models:
            print m
            for obj in m.objects.all():
                print "    ",obj
                obj.set_current()

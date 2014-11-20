#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from santaclara_base.models import Icon,IconFamily

class Command(BaseCommand):
    help = 'Set icon family'

    def handle(self, *args, **options):
        family_id=int(args[0])
        begin_id=int(args[1])
        end_id=int(args[2])
        print family_id,begin_id,end_id
        
        family=IconFamily.objects.get(id=family_id)
        icons=Icon.objects.all().filter(id__in=range(begin_id,end_id+1))
        for icon in icons:
            icon.family=family
            icon.save()
            print "set %s in %s" % (icon.html,family)

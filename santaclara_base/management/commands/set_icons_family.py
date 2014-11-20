#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from santaclara_base.models import Icon,IconFamily

class Command(BaseCommand):
    help = 'Set icon family'

    def handle(self, *args, **options):
        family_id=int(arg[0])
        begin_id=int(arg[1])
        end_id=int(arg[2])
        print family_id,begin_id,end_id
        
        family=IconFamily.objects.get(id=family_id)
        for i in range(begin_id,end_id+1):
            icon=Icon.objects.get(id=i)
            icon.family=family
            icon.save()
            print "set %s in %s" % (icon.html,family)

# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from santaclara_base.annotability import annotator,DisableAnnotationAnnotator,AllowForOwnerAnnotator,AllowForStaffAnnotator
from santaclara_base.taggability import taggator,DisableTagTaggator,AllowForOwnerTaggator,AllowForStaffTaggator

import santaclara_base.settings as settings

import santaclara_base.utility

# Create your models here.

import re
import datetime

RE_TAG=re.compile(r'\[.*?\]')
RE_NOTWORD=re.compile(r'[- _(){}\[\]=+:;\'",.?!«»`]+')

class Modifiable(object):
    def get_subcontext(self):
        return unicode(self.__class__)+"s"

    def get_absolute_url(self):
        return settings.SANTACLARA_BASE_CONTEXT+"/"+self.get_subcontext()+"/%d" % self.id

    def get_json_url(self):
        return settings.SANTACLARA_BASE_CONTEXT+"/json/"+self.get_subcontext()+"/%d" % self.id

    def get_update_url(self):
        return self.get_absolute_url()+"/update"

    def get_delete_url(self):
        return self.get_absolute_url()+"/delete"

    def get_json_update_url(self):
        return self.get_json_url()+"/update"

    def get_json_delete_url(self):
        return self.get_json_url()+"/delete"

class PositionAbstract(models.Model): 
    pos = models.PositiveIntegerField()
    class Meta:
        abstract = True

class TimestampAbstract(models.Model):
    created_by  = models.ForeignKey(User,related_name="%(app_label)s_%(class)s_created_by_set",editable=False)
    modified_by = models.ForeignKey(User,related_name="%(app_label)s_%(class)s_modified_by_set",editable=False)
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def submit_date(self):
        return self.created

    def user(self):
        return self.created_by


class VersionManager(models.Manager):
    def all_valid(self):
        return self.all().filter(valid=True)

    def order_by_last_modified(self):
        return self.order_by('last_modified')

class Version(TimestampAbstract,Modifiable):
    valid = models.BooleanField(default=True)
    text = models.TextField()
    label = models.CharField(max_length="128",default=lambda: datetime.datetime.now().strftime("%Y%m%d.%H%M%S.%f"))
    is_current = models.BooleanField(default=False,editable=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')
    objects = VersionManager()

    class Meta:
        ordering = [ 'id' ]

    def __unicode__(self): 
        #S="created by "+unicode(self.created_by)+" "+unicode(self.created)
        #S+=", modified by "+unicode(self.modified_by)+" "+unicode(self.last_modified)
        S=unicode(self.content_object)+u" v. "+self.label
        if self.is_current:
            S+=u" (current)"
        return S

    def count_characters(self):
        S=self.text
        S=S.replace("\n","")
        S=RE_TAG.sub(u"",S)
        return len(S)

    def count_words(self):
        S=self.text
        S=S.replace("\n","")
        S=RE_TAG.sub(u"",S).strip()
        return len(filter(bool,RE_NOTWORD.split(S)))

# moderator.register(Version,DisableCommentModerator)

class Location(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')
    ip_address = models.GenericIPAddressField(protocol='both',unpack_ipv4=True)

annotator.register(Location,AllowForStaffAnnotator)
taggator.register(Location,AllowForStaffTaggator)

class Annotation(TimestampAbstract,Modifiable):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')

    def __unicode__(self): 
        S="created by "+unicode(self.created_by)+" "+unicode(self.created)
        S+=", modified by "+unicode(self.modified_by)+" "+unicode(self.last_modified)
        return S

class Tag(models.Model):
    label = models.CharField(max_length=2048)

    def __unicode__(self): return self.label

    def get_absolute_url(self):
        return settings.SANTACLARA_BASE_CONTEXT+"/tags/%d-%s/" % (self.id,santaclara_base.utility.slugify(self.label))

annotator.register(Tag,AllowForStaffAnnotator)

class Tagging(TimestampAbstract,Modifiable):
    label = models.ForeignKey(Tag)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')

    def __unicode__(self): 
        return unicode(self.label)

class LocatedAbstract(models.Model):
    locations = generic.GenericRelation(Location)

    class Meta:
        abstract = True

    def save_ip_addresses(self,request):
        ips=santaclara_base.utility.get_request_ips(request)
        my_ct=ContentType.objects.get_for_model(self.__class__)
        for ip in ips:
            (obj,created)=Location.objects.get_or_create(content_type=my_ct,object_id=self.id,ip_address=ip)
    
    def ip_address(self):
        if not self.locations: return "none"
        t=[]
        for adr in self.locations.all():
            t.append(unicode(adr.ip_address))
        S=u", ".join(t)
        return S

class CommentManager(models.Manager):
    def all_public(self):
        return self.all().filter(is_public=True)

    def order_by_last_modified(self):
        return self.order_by('last_modified')

    def all_by_object(self,content_type_id,object_id):
        return self.all().filter(content_type__id=content_type_id,object_id=object_id)

class Comment(TimestampAbstract,LocatedAbstract,Modifiable):
    text = models.TextField()
    is_public = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')
    objects = CommentManager()

    class Meta:
        permissions = (
            ("can_moderate", "Can moderate comments"),
            )

    def __unicode__(self): 
        S="created by "+unicode(self.created_by)+" "+unicode(self.created)
        S+=", modified by "+unicode(self.modified_by)+" "+unicode(self.last_modified)
        return S

class VersionedAbstract(models.Model):
    versions = generic.GenericRelation(Version)
    current = models.ForeignKey(Version,editable=False,default=0,
                                related_name="%(app_label)s_%(class)s_current_set")
    class Meta:
        abstract = True

    def text(self):
        return self.current.text

    def set_current(self):
        qset=self.versions.order_by('-last_modified')
        if not qset: return
        for v in qset:
            if v.valid:
                if v==self.current:
                    self.current.is_current=True
                    self.current.save()
                    return
                v.is_current=True
                v.save()
                self.current.is_current=False
                self.current.save()
                self.current=v
                self.save()
                return
        v=qset[0]
        v.valid=True
        v.save()
        if v==self.current:
            self.current.is_current=True
            self.current.save()
            return
        self.current.is_current=False
        self.current.save()
        self.current=v
        self.save()

    def save_text(self,request,text,as_new_version=True):
        if self.current.id==0:
            as_new_version=True
        if as_new_version:
            v = Version(content_object=self,created_by=request.user,
                        modified_by=request.user,is_current=True,
                        valid=True,text=text )
            v.save()
            self.current.is_current=False
            self.current.save()
            self.current=v
            self.save()
            return
        self.current.text = text
        self.current.modified_by = request.user
        self.current.save()

    def count_characters(self):
        if self.current.id==0: return 0
        return self.current.count_characters()

    def count_words(self):
        if self.current.id==0: return 0
        return self.current.count_words()

    def count_versions(self):
        return self.versions.count()

    def version_number(self):
        return self.current.label

    def last_modified(self):
        return self.current.last_modified

class DisplayPropertyName(models.Model):
    name = models.CharField(max_length=2048)

    def __unicode__(self): return self.name

class DisplayPropertyScope(models.Model):
    name = models.CharField(max_length=2048)

    def __unicode__(self): return self.name

class DisplayPropertyList(models.Model):
    scope = models.ForeignKey(DisplayPropertyScope)
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type','object_id')

class DisplayProperty(models.Model):
    list = models.ForeignKey(DisplayPropertyList)
    name = models.ForeignKey(DisplayPropertyName)
    value = models.CharField(max_length=2048)

class DisplayedAbstract(models.Model):
    property_lists = generic.GenericRelation(DisplayPropertyList)

    class Meta:
        abstract = True



# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.html import format_html
from django.utils.safestring import SafeUnicode

from santaclara_base.annotability import annotator,DisableAnnotationAnnotator,AllowForOwnerAnnotator,AllowForStaffAnnotator
from santaclara_base.taggability import taggator,DisableTagTaggator,AllowForOwnerTaggator,AllowForStaffTaggator

import santaclara_base.settings as settings

import santaclara_base.utility

# Create your models here.

import re
import datetime

RE_TAG=re.compile(r'\[.*?\]')
RE_NOTWORD=re.compile(r'[- _(){}\[\]=+:;\'",.?!«»`]+')

class DefaultUrl(object):
    def get_id(self):
        return unicode(self.id)

    def get_semantic_id(self):
        u=santaclara_base.utility.slugify(unicode(self))
        return "%d-%s" % (self.id,u)

    def url_section(self): 
        return unicode(self.__class__.__name__).lower()

    def app_section(self): 
        return unicode(self._meta.app_label)
    
    def get_absolute_url(self):
        return u"/%s/%s/%s" % (self.app_section(),self.url_section(),self.get_semantic_id()) 

    def get_json_url(self):
        return u"/%s/json/%s/%s" % (self.app_section(),self.url_section(),self.get_id()) 

    def get_update_url(self):
        return self.get_absolute_url()+"/update"

    def get_delete_url(self):
        return self.get_absolute_url()+"/delete"
        
    def get_json_short_url(self):
        return self.get_json_url()+"/short"

    def get_json_full_url(self):
        return self.get_json_url()+"/full"

    def get_json_update_url(self):
        return self.get_json_url()+"/update"

    def get_json_delete_url(self):
        return self.get_json_url()+"/delete"
        
    def get_admin_url(self):
        return u"/admin/%s/%s/%s" % (self.app_section(),self.url_section(),self.get_id()) 

class PositionAbstract(models.Model): 
    pos = models.PositiveIntegerField()
    class Meta:
        abstract = True

def position_rel_factory(father_class,child_class,father_is_root=False):
    father_class_name=father_class.__name__.lower()
    child_class_name=child_class.__name__.lower()

    foreign_keys = []
    for field in child_class._meta.fields:
        if isinstance(child_class._meta.get_field_by_name(field.name)[0], models.ForeignKey):
            if field.rel.to == father_class:
                foreign_keys.append(field.name)
    if not foreign_keys:
        raise Exception("%s has no ForeignKey to %s",child_class,father_class)

    if len(foreign_keys)>1:
        raise Exception("%s has too many ForeignKey to %s",child_class,father_class)

    parent_field=foreign_keys[0]

    def new_CHILD_pos(self):
        child_set=getattr(self,child_class_name+"_set")
        pos=child_set.all().aggregate(Max('pos'))['pos__max']
        if not pos: return 1
        return pos+1

    def shift_CHILD_from(self,first_pos):
        child_set=getattr(self,child_class_name+"_set")
        n=first_pos+1
        for child in child_set.filter(pos__gte=first_pos).order_by("pos"):
            child.pos=n
            child.save()
            n+=1

    def normalize_CHILD_pos(self):
        child_set=getattr(self,child_class_name+"_set")
        n=1
        for child in child_set.all().order_by("pos"):
            child.pos=n
            child.save()
            n+=1

    def siblings_CHILD(self):
        child_set=getattr(self,child_class_name+"_set")
        return child_set.all()

    setattr(father_class,"new_"+child_class_name+"_pos",new_CHILD_pos)
    setattr(father_class,"shift_"+child_class_name+"_from",shift_CHILD_from)
    setattr(father_class,"normalize_"+child_class_name+"_pos",normalize_CHILD_pos)
    setattr(father_class,"siblings_"+child_class_name,siblings_CHILD)

    if father_is_root or not hasattr(father_class,"pos_previous"):
        def pos_previous(self):
            parent=getattr(self,parent_field)
            child_set=getattr(parent,child_class_name+"_set")
            return child_set.filter(pos__lt=self.pos).order_by('pos').last()
    else:
        def pos_previous(self):
            parent=getattr(self,parent_field)
            child_set=getattr(parent,child_class_name+"_set")
            child_prev=child_set.filter(pos__lt=self.pos).order_by('pos').last()
            if child_prev: return child_prev
            parent_prev=parent.pos_previous()
            while parent_prev:
                parent_prev_child_set=getattr(parent_prev,child_class_name+"_set")
                parent_prev_last_child=parent_prev_child_set.all().order_by('pos').last()
                if parent_prev_last_child: break
                parent_prev=parent_prev.pos_previous()
            if not parent_prev: return None
            return parent_prev_last_child

    if father_is_root or not hasattr(father_class,"full_pos"):
        def full_pos(self):
            return "%d" % self.pos
    else:
        def full_pos(self):
            parent=getattr(self,parent_field)
            return "%s.%d" % (parent.full_pos(),self.pos)

    if father_is_root or not hasattr(father_class,"pos_next"):
        def pos_next(self):
            parent=getattr(self,parent_field)
            child_set=getattr(parent,child_class_name+"_set")
            return child_set.filter(pos__lt=self.pos).order_by('pos').last()
    else:
        def pos_next(self):
            parent=getattr(self,parent_field)
            child_set=getattr(parent,child_class_name+"_set")
            child_next=child_set.filter(pos__gt=self.pos).order_by('pos').first()
            if child_next: return child_next
            parent_next=parent.pos_next()
            while parent_next:
                parent_next_child_set=getattr(parent_next,child_class_name+"_set")
                parent_next_first_child=parent_next_child_set.all().order_by('pos').first()
                if parent_next_first_child: break
                parent_next=parent_next.pos_next()
            if not parent_next: return None
            return parent_next_first_child

    def pos_insert(self,parent,before):
        f_shift=getattr(parent,"shift_"+child_class_name+"_from")
        f_shift(before)
        setattr(self,parent_field,parent)
        self.pos=before
        self.save()
        f_normalize=getattr(parent,"normalize_"+child_class_name+"_pos")
        f_normalize()

    def pos_append(self,parent):
        f_new=getattr(parent,"new_"+child_class_name+"_pos")
        pos=f_new()
        setattr(self,parent_field,parent)
        self.pos=pos
        self.save()
        f_normalize=getattr(parent,"normalize_"+child_class_name+"_pos")
        f_normalize()

    setattr(child_class,"pos_previous",pos_previous)
    setattr(child_class,"pos_next",pos_next)
    setattr(child_class,"pos_insert",pos_insert)
    setattr(child_class,"pos_append",pos_append)
    setattr(child_class,"full_pos",full_pos)

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

class Version(TimestampAbstract,DefaultUrl):
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

class Annotation(TimestampAbstract,DefaultUrl):
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
        return settings.SANTACLARA_BASE_CONTEXT+"/tag/%d-%s/" % (self.id,santaclara_base.utility.slugify(self.label))

annotator.register(Tag,AllowForStaffAnnotator)

class Tagging(TimestampAbstract,DefaultUrl):
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

class Comment(TimestampAbstract,LocatedAbstract,DefaultUrl):
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

    def save(self, *args, **kwargs):
        models.Model.save(self, *args, **kwargs)
        qset=self.versions.order_by('-created')
        if not qset: return
        selected=False
        for v in qset:
            if selected:
                v.is_current=False
                v.save()
                continue
            if not v.valid:
                v.is_current=False
                v.save()
                continue
            selected=True
            if v==self.current:
                self.current.is_current=True
                self.current.save()
                continue
            v.is_current=True
            v.save()
            self.current.is_current=False
            self.current.save()
            self.current=v
        if selected:
            models.Model.save(self, *args, **kwargs)
            return
        for v in qset:
            v.is_current=False
            v.save()
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
        models.Model.save(self, *args, **kwargs)

    def set_current(self):
        qset=self.versions.order_by('-last_modified')
        if not qset: return
        selected=False
        for v in qset:
            if selected:
                v.is_current=False
                v.save()
                continue
            if not v.valid:
                v.is_current=False
                v.save()
                continue
            selected=True
            if v==self.current:
                self.current.is_current=True
                self.current.save()
                continue
            v.is_current=True
            v.save()
            self.current.is_current=False
            self.current.save()
            self.current=v
        if selected:
            self.save()
            return
        for v in qset:
            v.is_current=False
            v.save()
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


###

RE_NAME_SEP=re.compile("('| |-)")

class LabeledAbstract(models.Model):
    label = models.SlugField(unique=True)
    description = models.CharField(max_length=1024)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.label)

    def clean(self,*args,**kwargs):
        self.label = self.label.lower()
        super(LabeledAbstract, self).clean(*args, **kwargs)

class NameFormat(LabeledAbstract):
    pattern = models.CharField(max_length=1024)

    class Meta:
        ordering = ["label"]

    def save(self, *args, **kwargs):
        super(NameFormat, self).save(*args, **kwargs)
        for coll in self.long_format_set.all():
            coll.save()
        for coll in self.short_format_set.all():
            coll.save()
        for coll in self.ordering_format_set.all():
            coll.save()
        for coll in self.list_format_set.all():
            coll.save()

class NameType(LabeledAbstract): pass

class NameFormatCollection(LabeledAbstract):
    long_format = models.ForeignKey(NameFormat,related_name='long_format_set')
    short_format = models.ForeignKey(NameFormat,related_name='short_format_set')
    list_format = models.ForeignKey(NameFormat,related_name='list_format_set')
    ordering_format = models.ForeignKey(NameFormat,related_name='ordering_format_set')

    def save(self, *args, **kwargs):
        super(NameFormatCollection, self).save(*args, **kwargs)
        for character in self.character_set.all():
            character.update_cache()

    ### Sintassi dei formati
    #   {{<name_type>}}: <name_type> 
    #   {{C|<name_type>}}: <name_type> (capitalized)
    #   {{V|<name_type>}}: <name_type> (capitalized except von, de, ecc.)
    #   {{L|<name_type>}}: <name_type> (lowered)
    #   {{U|<name_type>}}: <name_type> (uppered)
    #   {{A|<name_type>}}: <name_type> as integer in arabic 
    #   {{R|<name_type>}}: <name_type> as integer in roman upper
    #   {{N|<name_type>}}: <name_type> (lowered and with space => _)
    #   {{I|<name_type>}}: iniziali (Gian Uberto => G. U.)

    def required_name_types(self): 
        long_name=unicode(self.long_format.pattern)
        short_name=unicode(self.short_format.pattern)
        list_name=unicode(self.list_format.pattern)
        ordering_name=unicode(self.ordering_format.pattern)
        F=long_name+" "+short_name+" "+list_name+" "+ordering_name
        c=re.compile("{{.*?}}")
        format_list=c.findall(F)
        types=[]
        for t in format_list:
            t=t.replace("{{","").replace("}}","")
            if t[1]=="|":
                t=t[2:]
            types.append(t)
        types=list(set(types))
        name_types=NameType.objects.filter(label__in=types)
        return name_types

    def apply_formats(self,names):
        vons=["von","di","da","del","della","dell","dello","dei","degli","delle","de","d",
              "dal","dalla","dall","dallo","dai","dagli","dalle","al","ibn"]
        romans=["I","II","III","IV","V","VI","VII","VIII","IX","X",
                "XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX",
                "XXI","XXII","XXIII","XXIV","XXV","XXVI","XXVII","XXVIII","XXIX","XXX",
                "XXXI","XXXII","XXXIII","XXXIV","XXXV","XXXVI","XXXVII","XXXVIII","XXXIX","XL",
                "XLI","XLII","XLIII","XLIV","XLV","XLVI","XLVII","XLVIII","XLIX","L"]

        long_name=unicode(self.long_format.pattern)
        short_name=unicode(self.short_format.pattern)
        list_name=unicode(self.list_format.pattern)
        ordering_name=unicode(self.ordering_format.pattern)
        for key,val in names.items():
            val_f={}
            t=RE_NAME_SEP.split(val)
            #t=map(lambda x: x.capitalize(),RE_NAME_SEP.split(val))
            vons_t=[]
            norm_t=[]
            for x in t:
                if x.lower() in vons:
                    vons_t.append(x.lower())
                else:
                    if len(x)==1 and x.isalpha():
                        vons_t.append(x+".")
                    else:
                        vons_t.append(x)
                if len(x)==1 and x.isalpha():
                    norm_t.append(x+".")
                else:
                    norm_t.append(x)
                    
            cap_t=map(lambda x: x.capitalize(),norm_t)
            val_norm="".join(norm_t)
            val_f["L"]=val.lower()
            val_f["U"]=val.upper()
            val_f["N"]=val.lower().replace(" ","_")
            val_f["I"]=". ".join(map(lambda x: x[0].upper(),filter(bool,val.split(" "))))+"."
            val_f["C"]="".join(cap_t)
            val_f["V"]="".join(vons_t)

            if val.isdigit():
                val_f["R"]=romans[int(val)-1]
                val_f["A"]="%3.3d" % int(val)
            else:
                val_f["R"]=""
                val_f["A"]=""

            long_name=long_name.replace("{{"+key+"}}",val_norm)
            short_name=short_name.replace("{{"+key+"}}",val_norm)
            list_name=list_name.replace("{{"+key+"}}",val_norm)
            ordering_name=ordering_name.replace("{{"+key+"}}",val_norm)

            for k in "VALURNIC":
                long_name=long_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                short_name=short_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                list_name=list_name.replace("{{"+k+"|"+key+"}}",val_f[k])
                ordering_name=ordering_name.replace("{{"+k+"|"+key+"}}",val_f[k])

        return long_name,short_name,list_name,ordering_name

class IconFamily(models.Model):
    name = models.CharField(max_length=2048)

    def __unicode__(self): return self.name

    class Meta:
        ordering = [ "name" ]

class Icon(models.Model):
    family = models.ForeignKey(IconFamily)
    html = models.CharField(max_length=2048)

    def __unicode__(self): return SafeUnicode(self.html)

    class Meta:
        ordering = [ "id" ]

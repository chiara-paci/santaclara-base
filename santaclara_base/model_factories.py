from django.db.models import Max

def position_rel_factory(father_class,child_class,father_is_root=False):
    father_class_name=father_class.__name__.lower()
    child_class_name=child_class.__name__.lower()

    foreign_keys = []

    for field in child_class._meta.get_fields(include_parents=True):
        if not field.is_relation: continue
        if not field.many_to_one: continue
        if field.related_model == father_class:
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

    father_map=[ ("new_"+child_class_name+"_pos", new_CHILD_pos),
                 ("shift_"+child_class_name+"_from", shift_CHILD_from),
                 ("normalize_"+child_class_name+"_pos", normalize_CHILD_pos),
                 ("siblings_"+child_class_name, siblings_CHILD) ]

    for fname,f in father_map:
        if not hasattr(father_class,fname):
            setattr(father_class,fname,f)

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

    child_map=[ ("pos_previous",pos_previous),
                ("pos_next",pos_next),
                ("pos_insert",pos_insert),
                ("pos_append",pos_append),
                ("full_pos",full_pos)]

    for fname,f in child_map:
        if not hasattr(child_class,fname):
            setattr(child_class,fname,f)


class Taggator(object):
    def __init__(self): pass

    def allow(self,tag,content_object,request):
        return True

class DisableTagTaggator(Taggator):
    def allow(self,tag,content_object,request):
        return False

class AllowForOwnerTaggator(Taggator):
    def allow(self,tag,content_object,request):
        if not request.user.is_authenticated(): return False
        try:
            if callable(content_object.user):
                user=content_object.user()
            else:
                user=content_object.user
        except AttributeError, e:
            return False
        return (user.id==request.user.id)
    

class AllowForStaffTaggator(Taggator):
    def allow(self,tag,content_object,request):
        if not request.user.is_authenticated(): return False
        return (request.user.is_staff())

class Taggable(dict):
    def __init__(self):
        dict.__init__(self)
        self.default=DisableTagTaggator()

    def register(self,model,taggator):
        if not self.has_key(model):
            self[model]=[]
        self[model].append(taggator())

    def allow(self,request,tag):
        model=type(tag.content_object)
        if not self.has_key(model):
            return self.default.allow(tag,tag.content_object,request)
        for taggator in self[model]:
            if taggator.allow(tag,tag.content_object,request):
                return True
        return False

taggator=Taggable()


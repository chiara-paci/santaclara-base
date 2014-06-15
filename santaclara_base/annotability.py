class Annotator(object):
    def __init__(self): pass

    def allow(self,annotation,content_object,request):
        return True

class DisableAnnotationAnnotator(Annotator):
    def allow(self,annotation,content_object,request):
        return False

class AllowForOwnerAnnotator(Annotator):
    def allow(self,annotation,content_object,request):
        if not request.user.is_authenticated(): return False
        try:
            if callable(content_object.user):
                user=content_object.user()
            else:
                user=content_object.user
        except AttributeError, e:
            return False
        return (user.id==request.user.id)

class AllowForStaffAnnotator(Annotator):
    def allow(self,annotation,content_object,request):
        if not request.user.is_authenticated(): return False
        return (request.user.is_staff())

class Annotable(dict):
    def __init__(self):
        dict.__init__(self)
        self.default=DisableAnnotationAnnotator()

    def register(self,model,annotator):
        if not self.has_key(model):
            self[model]=[]
        self[model].append(annotator())

    def allow(self,request,annotation):
        model=type(annotation.content_object)
        if not self.has_key(model):
            return self.default.allow(annotation,annotation.content_object,request)
        for annotator in self[model]:
            if annotator.allow(annotation,annotation.content_object,request):
                return True
        return False

annotator=Annotable()


class CommentModerator(object):
    def __init__(self): pass

    def allow(self,comment,content_object,request):
        return True

class DisableCommentModerator(CommentModerator):
    def allow(self,comment,content_object,request):
        return False

class AuthenticatedCommentModerator(CommentModerator):
    def allow(self,comment, content_object, request):
        return request.user.is_authenticated()

class AllowForStaffModerator(CommentModerator):
    def allow(self,comment, content_object, request):
        if not request.user.is_authenticated(): return False
        return (request.user.is_staff())

# class ModerationCommentModerator(CommentModerator):
#     enable_field = 'is_open'
    
#     def allow(self,comment, content_object, request):
#         return request.user.is_authenticated()

#     def moderate(self,comment, content_object, request):
#         return not request.user.is_superuser

class Moderable(dict):
    def __init__(self):
        dict.__init__(self)
        self.default=DisableCommentModerator()

    def register(self,model,moderator):
        if not self.has_key(model):
            self[model]=[]
        self[model].append(moderator())

    def allow(self,request,comment):
        model=type(comment.content_object)
        if not self.has_key(model):
            return self.default.allow(comment,comment.content_object,request)
        for moderator in self[model]:
            if moderator.allow(comment,comment.content_object,request):
                return True
        return False

moderator=Moderable()

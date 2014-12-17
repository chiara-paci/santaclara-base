def slugify(S):
    t=filter(lambda x: x.isalnum() or x==' ',unicode(S))
    t=t.replace(" ","-")
    t=t.lower()
    t=t.strip("-")
    return t

def alphabetic_lower(num):
    base="abcdefghijklmnopqrstuvwxyz"
    while num>=len(base):
        num-=len(base)
    return base[num]

def get_request_ips(request):
    v_ip=[ request.META["REMOTE_ADDR"] ]
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        v_ip+=request.META.has_key('HTTP_X_FORWARDED_FOR').split(",")
    v_ip=map(lambda x: x.strip(),v_ip)
    return v_ip

# def request_log(request,application,label,oid,human):
#     v_date=datetime.datetime.now()
#     v_ip=request.META["REMOTE_ADDR"]
#     if request.META.has_key("HTTP_USER_AGENT"):
#         v_browser=request.META["HTTP_USER_AGENT"]
#     else:
#         v_browser="-"
#     if request.META.has_key("HTTP_REFERER"):
#         v_ref=request.META["HTTP_REFERER"]
#     else:
#         v_ref="-"
#     v=Visita(application=application,label=label,objid=oid,objhuman=human,
#              v_date=v_date,v_ip=v_ip,v_browser=v_browser,v_ref=v_ref)
#     v.save()

def numberize(cat,num):
    if cat=="arabic":
        return num
    if cat in ["alpha","bigalpha"]:
        if cat=="alpha": base="a"
        else: base="A"
        d=num-1
        L=[]
        while d>=26:
            m=d%26
            d=d/26-1
            L.append(m)
        L.append(d%26)
        L.reverse()
        T=reduce(lambda a,b: a+b,map(lambda x: chr(ord(base)+x),L))
        return T
    if cat in [ "roman","bigroman" ]:
        def f(d,b,p10,p05,p01):
            s=""                
            if d>=9*b:
                s+=p01+p10
                d-=9*b
            elif d>=5*b:
                s+=p05
                d-=5*b
                while d>=b:
                    s+=p01
                    d-=b
            elif d>=4*b:
                s+=p01+p05
                d-=4*b
            else:
                while d>=b:
                    s+=p01
                    d-=b
            return (s,d)
        D=num
        S=""
        while D>=1000:
            S+="M"
            D-=1000
        (s,D)=f(D,100,"M","D","C")
        S+=s
        (s,D)=f(D,10,"C","L","X")
        S+=s
        (s,D)=f(D,1,"X","V","I")
        S+=s
        if cat=="roman":
            return S.lower()
        else:
            return S
    return num

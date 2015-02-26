import django.dispatch

position_changed = django.dispatch.Signal(providing_args=["instance"])
valid_changed = django.dispatch.Signal(providing_args=["instance"])

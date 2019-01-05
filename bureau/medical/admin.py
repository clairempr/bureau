from django.contrib import admin

from .models import Ailment, AilmentType

admin.site.register(Ailment)
admin.site.register(AilmentType)

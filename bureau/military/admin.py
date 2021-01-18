from django.contrib import admin

from .models import Regiment

class RegimentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'vrc', 'us', 'usct')
    list_filter = ('vrc', 'us', 'usct', 'state',)
    ordering = ('number', 'name')
    search_fields = ('name',)
    save_on_top = True

admin.site.register(Regiment, RegimentAdmin)

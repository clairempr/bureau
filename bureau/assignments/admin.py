from django.contrib import admin

from .models import Assignment, Position

class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'employee')
    list_filter = ('positions', )
    search_fields = ('description', )
    raw_id_fields = ('places', )
    save_on_top = True

admin.site.register(Assignment, AssignmentAdmin)


class PositionAdmin(admin.ModelAdmin):
    ordering = ('name',)

admin.site.register(Position)

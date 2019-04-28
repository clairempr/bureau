from django.contrib import admin

from .models import Assignment, Position

class AssignmentAdmin(admin.ModelAdmin):
    save_on_top = True


admin.site.register(Assignment, AssignmentAdmin)


admin.site.register(Position)

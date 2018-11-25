from django.contrib import admin

from .models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'bureau_state', 'vrc')
    list_filter = ('bureau_states', 'vrc',
                   # 'vrc_units'
                   )

    def bureau_state(self, obj):
        return obj.bureau_state_list()

admin.site.register(Employee, EmployeeAdmin)

from django.contrib import admin

from .models import Employee

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'bureau_state', 'vrc')
    list_filter = ('bureau_states', 'vrc', 'regiments')

    def save_model(self, request, obj, form, change):
        # Make sure someone who's a member of a VRC regiment has VRC set to true
        if form.cleaned_data['regiments'].filter(vrc=True):
            obj.vrc = True

        super(EmployeeAdmin, self).save_model(request, obj, form, change)

    def bureau_state(self, obj):
        return obj.bureau_state_list()

admin.site.register(Employee, EmployeeAdmin)

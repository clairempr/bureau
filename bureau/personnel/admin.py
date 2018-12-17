import string

from django.contrib import admin

from .models import Employee

class FirstLetterListFilter(admin.SimpleListFilter):
    title = 'first letter'
    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        return [(letter, letter) for letter in list(string.ascii_uppercase)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(last_name__startswith=self.value())
        return queryset

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'bureau_state', 'vrc')
    list_filter = ('vrc', FirstLetterListFilter, 'bureau_states', 'regiments')
    search_fields = ('last_name', 'first_name', 'notes')
    list_per_page = 75
    save_on_top = True

    def save_model(self, request, obj, form, change):
        # Make sure someone who's a member of a VRC regiment has VRC set to true
        if form.cleaned_data['regiments'].filter(vrc=True):
            obj.vrc = True

        super(EmployeeAdmin, self).save_model(request, obj, form, change)

    def bureau_state(self, obj):
        return obj.bureau_state_list()


admin.site.register(Employee, EmployeeAdmin)

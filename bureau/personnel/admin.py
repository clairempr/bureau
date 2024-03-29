import string

from django.contrib import admin

from assignments.models import Assignment

from .models import Employee


YES_NO_LOOKUPS = (
            ('Yes', 'Yes'),
            ('No', 'No'),
)


class DateOfBirthFilledListFilter(admin.SimpleListFilter):
    title = 'date of birth filled'
    parameter_name = 'date_of_birth'

    def lookups(self, request, model_admin):
        return YES_NO_LOOKUPS

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'Yes':
                return queryset.filter(date_of_birth__isnull=False)
            if self.value() == 'No':
                return queryset.filter(date_of_birth__isnull=True)
        return queryset


class PlaceOfBirthFilledListFilter(admin.SimpleListFilter):
    title = 'place of birth filled'
    parameter_name = 'place_of_birth'

    def lookups(self, request, model_admin):
        return YES_NO_LOOKUPS

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'Yes':
                return queryset.filter(place_of_birth__isnull=False)
            if self.value() == 'No':
                return queryset.filter(place_of_birth__isnull=True)
        return queryset


class EmploymentYearListFilter(admin.SimpleListFilter):
    title = 'employment year'
    parameter_name = 'employment_year'

    def lookups(self, request, model_admin):
        if Assignment.objects.exists():
            min_year = Assignment.objects.filter(
                    start_date__isnull=False).order_by('start_date').first().start_date.date.year
            max_year = Assignment.objects.filter(end_date__isnull=False).order_by('end_date').last().end_date.date.year
            return [(year, year) for year in range(min_year, max_year + 1)]
        return []

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(pk__in=Employee.objects.employed_during_year(int(self.value())).values('pk'))
        return queryset


class FirstLetterListFilter(admin.SimpleListFilter):
    title = 'first letter'
    parameter_name = 'letter'

    def lookups(self, request, model_admin):
        return [(letter, letter) for letter in list(string.ascii_uppercase)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(last_name__startswith=self.value())
        return queryset


class USCTListFilter(admin.SimpleListFilter):
    title = 'USCT'
    parameter_name = 'usct'

    def lookups(self, request, model_admin):
        return YES_NO_LOOKUPS

    def queryset(self, request, queryset):
        if self.value():
            if self.value() == 'Yes':
                return queryset.filter(regiments__usct__exact=True).distinct()
            if self.value() == 'No':
                return queryset.filter(regiments__usct__exact=False).distinct()
        return queryset


class AssignmentInline(admin.TabularInline):
    model = Assignment
    ordering = ('start_date',)
    extra = 0
    raw_id_fields = ('places',)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'bureau_state', 'vrc', 'needs_backfilling', 'place_of_birth', 'age_in_1865',)
    list_filter = (DateOfBirthFilledListFilter, PlaceOfBirthFilledListFilter, EmploymentYearListFilter, 'vrc',
                   USCTListFilter, FirstLetterListFilter, 'bureau_states', 'ailments',
                   'penmanship_contest', 'colored', 'gender', 'union_veteran', 'confederate_veteran', 'slaveholder',
                   'needs_backfilling')
    search_fields = ('last_name', 'first_name', 'notes')
    raw_id_fields = ('place_of_birth', 'place_of_residence', 'place_of_death',)
    filter_horizontal = ('regiments',)
    inlines = [AssignmentInline, ]
    list_per_page = 75
    save_on_top = True

    def save_model(self, request, obj, form, change):
        # Make sure someone who's a member of a VRC regiment has VRC set to true
        if form.cleaned_data['regiments'].filter(vrc=True):
            obj.vrc = True

        super().save_model(request, obj, form, change)

    def bureau_state(self, obj):
        return obj.bureau_state_list()

    def age_in_1865(self, obj):
        return obj.calculate_age(1865)


admin.site.register(Employee, EmployeeAdmin)

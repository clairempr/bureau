from django.contrib.postgres.aggregates import StringAgg
from django.views.generic import ListView

from assignments.models import Assignment
from places.models import Place
from places.utils import get_place_or_none


class AssignmentListView(ListView):

    model = Assignment
    queryset = Assignment.objects.all()
    ordering = ['start_date', 'concatenated_titles', 'employee__last_name', 'employee__first_name']
    template_name = "assignments/assignment_list.html"

    def get_place(self):
        # If place is in kwargs, try to return the Place
        place_pk = self.kwargs.get('place')
        return get_place_or_none(place_pk) if place_pk else None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Put the specified Place object in the view context. If there wasn't one, it will be None
        context['place'] = self.get_place()
        return context

    def get_queryset(self):
        # If a place is specified, only return assignments in that exact place, not places in that place
        place = self.get_place()
        if place:
            queryset = Assignment.objects.in_place(place=place, exact=True)
        else:
            queryset = self.queryset

        # Annotate to order by position titles without duplicate entries when assignment has multiple positions
        return self.annotate_titles(queryset).order_by(*self.ordering)

    def annotate_titles(self, queryset):
        """
        Annotate to order by position titles without duplicate entries when assignment has multiple positions
        """

        # StringAgg is Postgres-only
        return queryset.annotate(concatenated_titles=StringAgg('positions__title', delimiter=''))


assignment_list_view = AssignmentListView.as_view()


class BureauHeadquartersAssignmentListView(AssignmentListView):

    def get_queryset(self):
        # Return Bureau Headquarters assignments only
        # Annotate to order by position titles without duplicate entries when assignment has multiple positions
        return self.annotate_titles(Assignment.objects.filter(bureau_headquarters=True)).order_by(*self.ordering)


bureau_headquarters_assignment_list_view = BureauHeadquartersAssignmentListView.as_view()

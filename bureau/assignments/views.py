from django.views.generic import ListView

from assignments.models import Assignment
from places.models import Place

class AssignmentListView(ListView):

    model = Assignment
    queryset = Assignment.objects.all()
    template_name = "assignments/assignment_list.html"

    def get_place(self):
        # If place is in kwargs and it's the pk of a Place, return the Place
        # otherwise return None
        place_pk = self.kwargs.get('place')
        if place_pk:
            try:
                return Place.objects.get(pk=place_pk)
            except Place.DoesNotExist:
                pass

        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Put the specified Place object in the view context. If there wasn't one, it will be None
        context['place'] = self.get_place()
        return context

    def get_queryset(self):
        # If a place is specified, only return assignments in that exact place, not places in that place
        place = self.get_place()
        if place:
            return Assignment.objects.in_place(place=place, exact=True).order_by('start_date')

        return self.queryset


assignment_list_view = AssignmentListView.as_view()

class BureauHeadquartersAssignmentListView(AssignmentListView):

    queryset = Assignment.objects.filter(bureau_headquarters=True).order_by('start_date')

    def get_queryset(self):
        # Return Bureau Headquarters assignments only
        return Assignment.objects.filter(bureau_headquarters=True).order_by('start_date')


bureau_headquarters_assignment_list_view = BureauHeadquartersAssignmentListView.as_view()

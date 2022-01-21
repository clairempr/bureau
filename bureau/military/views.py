from django.views.generic import DetailView, ListView

from military.models import Regiment


class RegimentDetailView(DetailView):

    model = Regiment


regiment_detail_view = RegimentDetailView.as_view()


class RegimentListView(ListView):

    model = Regiment
    paginate_by = 25
    slug_field = "name"
    slug_url_kwarg = "name"
    queryset = Regiment.objects.all()
    regiment_type = 'all_regiments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.regiment_type] = True
        search_text = self.request.GET.get('search_text')
        context['search_text'] = search_text if search_text else ''
        return context

    def get_queryset(self):
        search_text = self.request.GET.get('search_text')
        if search_text:
            return self.queryset.filter(name__icontains=search_text)

        return self.queryset


regiment_list_view = RegimentListView.as_view()


class ConfederateRegimentListView(RegimentListView):

    queryset = Regiment.objects.filter(confederate=True)
    regiment_type = 'confederate_regiments'


confederate_regiment_list_view = ConfederateRegimentListView.as_view()


class RegularArmyRegimentListView(RegimentListView):

    queryset = Regiment.objects.filter(us=True).exclude(usct=True).exclude(branch=Regiment.Branch.SHARPSHOOTERS)
    regiment_type = 'regular_army_regiments'


regular_army_regiment_list_view = RegularArmyRegimentListView.as_view()


class StateRegimentListView(RegimentListView):

    queryset = Regiment.objects.exclude(state__isnull=True)
    regiment_type = 'state_regiments'


state_regiment_list_view = StateRegimentListView.as_view()


class USCTRegimentListView(RegimentListView):

    queryset = Regiment.objects.filter(usct=True)
    regiment_type = 'usct_regiments'


usct_regiment_list_view = USCTRegimentListView.as_view()


class VRCRegimentListView(RegimentListView):

    queryset = Regiment.objects.filter(vrc=True)
    regiment_type = 'vrc_regiments'


vrc_regiment_list_view = VRCRegimentListView.as_view()

from django.views.generic import DetailView, ListView

from military.models import Regiment

class RegimentDetailView(DetailView):

    model = Regiment


regiment_detail_view = RegimentDetailView.as_view()


class RegimentListView(ListView):

    model = Regiment
    slug_field = "name"
    slug_url_kwarg = "name"
    regiment_type = 'all_regiments'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.regiment_type] = True
        return context


regiment_list_view = RegimentListView.as_view()


class VRCRegimentListView(RegimentListView):

    queryset = Regiment.objects.filter(vrc=True)
    regiment_type = 'vrc_regiments'


vrc_regiment_list_view = VRCRegimentListView.as_view()

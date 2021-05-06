from django.shortcuts import render
from django.views.generic import ListView
from rooms.models import Room

class SearchRoomView(ListView):
    template_name   = "search/view.html"
    paginate_by     = 6

    def get_context_data(self, *args, **kwargs):
        context             = super(SearchRoomView, self).get_context_data(*args, **kwargs)
        query               = self.request.GET.get('q')
        result_counter      = self.object_list.count()
        context['query']    = query
        context['count']    = result_counter
        return context
        
    def get_queryset(self, *args, **kwargs):
        request     = self.request
        method_dict = request.GET
        query       = method_dict.get('q', None)
        if query is not None:    
            return Room.objects.search(query)
        return Room.objects.all()
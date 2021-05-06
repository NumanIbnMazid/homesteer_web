from django.shortcuts import render
from django.views.generic import TemplateView

def home(request):
    return render(request, 'pages/home.html')

class PolicyView(TemplateView):
    template_name = 'pages/policy.html'
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class CustomLoginRequiredMixin(LoginRequiredMixin):
    """Regular LoginRequiredMixin, but without ?next= appending to login page url"""
    redirect_field_name = ''


class LandingView(TemplateView):
    template_name = 'shallwe_app/index.html'


class SampleRequireSessionLoginView(CustomLoginRequiredMixin, TemplateView):
    login_url = 'landing'
    template_name = 'shallwe_app/protected-page.html'

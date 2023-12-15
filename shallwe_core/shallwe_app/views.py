from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView


class LoginRequiredMixinLandingPreset(LoginRequiredMixin):
    """Regular LoginRequiredMixin, but without ?next= appending to login page url"""
    redirect_field_name = ''
    login_url = 'page-landing'


class ReactAppServingView(TemplateView):
    template_name = 'index.html'


class LandingView(ReactAppServingView):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            # Redirect authenticated users to another page
            return redirect('page-setup')
        else:
            return super().dispatch(request, *args, **kwargs)


class SetupView(LoginRequiredMixinLandingPreset, ReactAppServingView):
    pass


class SearchView(LoginRequiredMixinLandingPreset, ReactAppServingView):
    pass


class ContactsView(LoginRequiredMixinLandingPreset, ReactAppServingView):
    pass


class SettingsView(LoginRequiredMixinLandingPreset, ReactAppServingView):
    pass

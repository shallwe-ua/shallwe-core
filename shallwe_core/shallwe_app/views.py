from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView


class LoginRequiredMixinLandingPreset(LoginRequiredMixin):
    redirect_field_name = ''    # Cancelling ?next= in URL
    login_url = 'page-landing'


class ReactAppServingView(TemplateView):
    template_name = 'index.html'


class GeneralLoginRequiredView(LoginRequiredMixinLandingPreset, ReactAppServingView):
    pass


class LandingView(ReactAppServingView):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            # Redirect authenticated users to another page
            return redirect('page-setup')
        else:
            return super().dispatch(request, *args, **kwargs)


class SetupView(GeneralLoginRequiredView):
    pass


class SearchView(GeneralLoginRequiredView):
    pass


class ContactsView(GeneralLoginRequiredView):
    pass


class SettingsView(GeneralLoginRequiredView):
    pass

from django.conf import settings
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
        if request.user.is_authenticated:
            if hasattr(request.user, 'profile'):
                return redirect('page-search')
            else:
                return redirect('page-setup')
        else:
            return super().dispatch(request, *args, **kwargs)


class SetupView(GeneralLoginRequiredView):
    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, 'profile'):
            return redirect('page-settings')
        else:
            return super().dispatch(request, *args, **kwargs)


class SearchView(GeneralLoginRequiredView):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('page-setup')
        else:
            return super().dispatch(request, *args, **kwargs)


class ContactsView(GeneralLoginRequiredView):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('page-setup')
        else:
            return super().dispatch(request, *args, **kwargs)


class SettingsView(GeneralLoginRequiredView):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'profile'):
            return redirect('page-setup')
        else:
            return super().dispatch(request, *args, **kwargs)

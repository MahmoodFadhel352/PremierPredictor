
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import MatchForm, PredictionForm

from .models import Team, Match, Prediction
# Create your views here.
# Home / Auth
class Home(LoginView):
    template_name = 'home.html'

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('match-index')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    return render(request, 'signup.html', {'form': form, 'error_message': error_message})

def about(request):
    return render(request, 'about.html')


# Teams
class TeamList(LoginRequiredMixin, ListView):
    model = Team
    template_name = "teams/index.html"


class TeamDetail(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "teams/detail.html"
class TeamCreate(LoginRequiredMixin, CreateView):
    model = Team
    fields = ['name', 'short_code', 'founded_year', 'logo']
    template_name = "main_app/team_form.html"
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
class TeamUpdate(LoginRequiredMixin, UpdateView):
    model = Team
    fields = ['name', 'short_code', 'founded_year', 'logo']
    template_name = "main_app/team_form.html"
    def get_queryset(self):
        return Team.objects.filter(created_by=self.request.user)

class TeamDelete(LoginRequiredMixin, DeleteView):
    model = Team
    success_url = '/teams/'
    template_name = "main_app/team_confirm_delete.html"
    def get_queryset(self):
        return Team.objects.filter(created_by=self.request.user)


# Matches
class MatchList(LoginRequiredMixin, ListView):
    model = Match
    template_name = "main_app/match_list.html"

class MatchDetail(LoginRequiredMixin, DetailView):
    model = Match
    template_name = "main_app/match_detail.html"

class MatchCreate(LoginRequiredMixin, CreateView):
    model = Match
    form_class = MatchForm
    template_name = "main_app/match_form.html"
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class MatchUpdate(LoginRequiredMixin, UpdateView):
    model = Match
    form_class = MatchForm
    template_name = "main_app/match_form.html"
    def get_queryset(self):
        return Match.objects.filter(created_by=self.request.user)

class MatchDelete(LoginRequiredMixin, DeleteView):
    model = Match
    success_url = '/matches/'
    template_name = "main_app/match_confirm_delete.html"
    def get_queryset(self):
        return Match.objects.filter(created_by=self.request.user)

# Predictions
class PredictionList(LoginRequiredMixin, ListView):
    model = Prediction
    template_name = "main_app/prediction_list.html"

class PredictionDetail(LoginRequiredMixin, DetailView):
    model = Prediction
    template_name = "main_app/prediction_detail.html"

class PredictionCreate(LoginRequiredMixin, CreateView):
    model = Prediction
    form_class = PredictionForm
    template_name = "main_app/prediction_form.html"
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PredictionUpdate(LoginRequiredMixin, UpdateView):
    model = Prediction
    form_class = PredictionForm
    template_name = "main_app/prediction_form.html"
    def get_queryset(self):
        # only edit your own prediction
        return Prediction.objects.filter(user=self.request.user)

class PredictionDelete(LoginRequiredMixin, DeleteView):
    model = Prediction
    success_url = '/predictions/'
    template_name = "main_app/prediction_confirm_delete.html"
    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user)

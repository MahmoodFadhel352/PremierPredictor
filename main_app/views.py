
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

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

class TeamDetail(LoginRequiredMixin, DetailView):
    model = Team

class TeamCreate(LoginRequiredMixin, CreateView):
    model = Team
    fields = ['name', 'short_code', 'founded_year', 'logo']

class TeamUpdate(LoginRequiredMixin, UpdateView):
    model = Team
    fields = ['name', 'short_code', 'founded_year', 'logo']

class TeamDelete(LoginRequiredMixin, DeleteView):
    model = Team
    success_url = '/teams/'


# Matches
class MatchList(LoginRequiredMixin, ListView):
    model = Match

class MatchDetail(LoginRequiredMixin, DetailView):
    model = Match

class MatchCreate(LoginRequiredMixin, CreateView):
    model = Match
    fields = ['home_team', 'away_team', 'kickoff_at', 'venue', 'status']

class MatchUpdate(LoginRequiredMixin, UpdateView):
    model = Match
    fields = ['home_score', 'away_score', 'status', 'venue', 'kickoff_at']

class MatchDelete(LoginRequiredMixin, DeleteView):
    model = Match
    success_url = '/matches/'


# Predictions
class PredictionList(LoginRequiredMixin, ListView):
    model = Prediction

class PredictionDetail(LoginRequiredMixin, DetailView):
    model = Prediction

class PredictionCreate(LoginRequiredMixin, CreateView):
    model = Prediction
    fields = ['match', 'pick', 'stake', 'model_key', 'p_home', 'p_draw', 'p_away']
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class PredictionUpdate(LoginRequiredMixin, UpdateView):
    model = Prediction
    fields = ['pick', 'stake']

class PredictionDelete(LoginRequiredMixin, DeleteView):
    model = Prediction
    success_url = '/predictions/'

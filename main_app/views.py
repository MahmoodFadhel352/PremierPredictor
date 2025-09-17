
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import MatchForm, PredictionForm, TeamForm
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.contrib import messages

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
    for field in form.fields.values():
        field.widget.attrs.update({'placeholder': field.label})
    return render(request, 'signup.html', {'form': form, 'error_message': error_message})

def about(request):
    return render(request, 'about.html')


# Teams
class TeamList(LoginRequiredMixin, ListView):
    model = Team
    template_name = "teams/index.html"
    queryset = Team.objects.order_by('name')

class TeamDetail(LoginRequiredMixin, DetailView):
    model = Team
    template_name = "teams/detail.html"
class TeamCreate(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm 
    template_name = "main_app/team_form.html"
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
class TeamUpdate(LoginRequiredMixin, UpdateView):
    model = Team
    form_class = TeamForm
    template_name = "main_app/team_form.html"
    def get_queryset(self):
        return Team.objects.filter(created_by=self.request.user)
    def form_valid(self, form):
        # If the “Remove logo” was checked, drop the file
        if self.request.POST.get("logo-clear"):
            if form.instance.logo:
                form.instance.logo.delete(save=False)
            form.instance.logo = None
        return super().form_valid(form)

class TeamDelete(LoginRequiredMixin, DeleteView):
    model = Team
    template_name = "main_app/team_confirm_delete.html"
    success_url = "/teams/"

    def get_queryset(self):
        # only allow deleting teams you created
        return Team.objects.filter(created_by=self.request.user)

    def post(self, request, *args, **kwargs):
        """
        Handle the POST explicitly and catch ProtectedError raised by model.delete().
        This is more robust than relying on DeleteView.delete() in some setups.
        """
        self.object = self.get_object()
        try:
            self.object.delete()
        except ProtectedError:
            blocking_matches = (
                Match.objects
                .filter(Q(home_team=self.object) | Q(away_team=self.object))
                .select_related("home_team", "away_team")
            )
            # Render a friendly page explaining what blocks the delete
            return render(
                request,
                "main_app/team_cannot_delete.html",
                {"team": self.object, "blocking_matches": blocking_matches},
            )
        return redirect(self.get_success_url())

# Matches
class MatchList(LoginRequiredMixin, ListView):
    model = Match
    template_name = "main_app/match_list.html"
    queryset = Match.objects.select_related('home_team', 'away_team', 'created_by').order_by('-kickoff_at')

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
    queryset = Prediction.objects.select_related('match', 'user', 'match__home_team', 'match__away_team').order_by('-created_at')

class PredictionDetail(LoginRequiredMixin, DetailView):
    model = Prediction
    template_name = "main_app/prediction_detail.html"

class PredictionCreate(LoginRequiredMixin, CreateView):
    model = Prediction
    form_class = PredictionForm
    template_name = "main_app/prediction_form.html"
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs
    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            return super().form_valid(form)
        except IntegrityError:
            form.add_error(None, "You already have a prediction for this match. Please edit the existing one.")
            return self.form_invalid(form)

class PredictionUpdate(LoginRequiredMixin, UpdateView):
    model = Prediction
    form_class = PredictionForm
    template_name = "main_app/prediction_form.html"
    def get_queryset(self):
        # only edit your own prediction
        return Prediction.objects.filter(user=self.request.user)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

class PredictionDelete(LoginRequiredMixin, DeleteView):
    model = Prediction
    success_url = '/predictions/'
    template_name = "main_app/prediction_confirm_delete.html"
    def get_queryset(self):
        return Prediction.objects.filter(user=self.request.user)

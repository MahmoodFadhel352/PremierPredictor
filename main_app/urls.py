from django.urls import path
from . import views

urlpatterns = [
    # Home / Auth
    path('', views.Home.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('accounts/signup/', views.signup, name='signup'),

    # Teams
    path('teams/', views.TeamList.as_view(), name='team-index'),
    path('teams/<int:pk>/', views.TeamDetail.as_view(), name='team-detail'),
    path('teams/create/', views.TeamCreate.as_view(), name='team-create'),
    path('teams/<int:pk>/update/', views.TeamUpdate.as_view(), name='team-update'),
    path('teams/<int:pk>/delete/', views.TeamDelete.as_view(), name='team-delete'),

    # Matches
    path('matches/', views.MatchList.as_view(), name='match-index'),
    path('matches/<int:pk>/', views.MatchDetail.as_view(), name='match-detail'),
    path('matches/create/', views.MatchCreate.as_view(), name='match-create'),
    path('matches/<int:pk>/update/', views.MatchUpdate.as_view(), name='match-update'),
    path('matches/<int:pk>/delete/', views.MatchDelete.as_view(), name='match-delete'),

    # Predictions
    path('predictions/', views.PredictionList.as_view(), name='prediction-index'),
    path('predictions/<int:pk>/', views.PredictionDetail.as_view(), name='prediction-detail'),
    path('predictions/create/', views.PredictionCreate.as_view(), name='prediction-create'),
    path('predictions/<int:pk>/update/', views.PredictionUpdate.as_view(), name='prediction-update'),
    path('predictions/<int:pk>/delete/', views.PredictionDelete.as_view(), name='prediction-delete'),
]

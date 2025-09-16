from django import forms
from django.core.exceptions import ValidationError
from .models import Match
from .models import Prediction, Team
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "short_code", "founded_year", "logo"]
        widgets = {
            # Use FileInput so Django doesn't render the "Currently / Clear / Change" block
            "logo": forms.FileInput(attrs={
                "accept": ".svg,.png,.jpg,.jpeg",
                "class": "file-input"
            }),
        }
        labels = {
            "name": "Name",
            "short_code": "Short code",
            "founded_year": "Founded year",
            "logo": "Logo",
        }
class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['home_team', 'away_team', 'kickoff_at', 'venue', 'status']
        widgets = {
            # HTML5 picker; note the "T" between date and time
            'kickoff_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Accept the value the datetime-local control posts (e.g. 2025-09-22T19:30)
        self.fields['kickoff_at'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M']

class PredictionForm(forms.ModelForm):
    class Meta:
        model = Prediction
        fields = ["match", "pick", "p_home", "p_draw", "p_away"]
        widgets = {
            "pick": forms.RadioSelect,
            "p_home": forms.NumberInput(attrs={"min": "0", "max": "1", "step": "0.01", "placeholder": "e.g. 0.45"}),
            "p_draw": forms.NumberInput(attrs={"min": "0", "max": "1", "step": "0.01", "placeholder": "e.g. 0.30"}),
            "p_away": forms.NumberInput(attrs={"min": "0", "max": "1", "step": "0.01", "placeholder": "e.g. 0.25"}),
        }
        labels = {
            "match": "Match",
            "pick": "Your pick",
            "p_home": "Probability of home win",
            "p_draw": "Probability of draw",
            "p_away": "Probability of away win",
        }
        help_texts = {
            "pick": "Choose the outcome you think will happen.",
            "p_home": "Optional. Use a number between 0 and 1 (e.g., 0.45).",
            "p_draw": "Optional. Use a number between 0 and 1.",
            "p_away": "Optional. Use a number between 0 and 1.",
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if "pick" in self.fields:
            choices = list(self.fields["pick"].choices)
            if choices and choices[0][0] in ("", None):  # first one is the blank
                self.fields["pick"].choices = choices[1:]

    def clean(self):
        cleaned = super().clean()
        ph, pd, pa = cleaned.get("p_home"), cleaned.get("p_draw"), cleaned.get("p_away")
        match = cleaned.get("match")

        #Probability validation
        provided = [v for v in (ph, pd, pa) if v is not None]
        if provided:
            if any(v < 0 or v > 1 for v in provided):
                raise forms.ValidationError("Probabilities must be between 0 and 1.")
            total = (ph or 0) + (pd or 0) + (pa or 0)
            if abs(total - 1.0) > 0.05:  # 5% tolerance
                raise forms.ValidationError("Probabilities should add up to ~1.0 (±0.05).")

        #Prevent duplicate predictions by same user for same match
        if self.user and match:
            qs = Prediction.objects.filter(user=self.user, match=match)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError("You already have a prediction for this match. Please edit it instead.")

        return cleaned

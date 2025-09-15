from django import forms
from .models import Match
from .models import Prediction
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

    def clean(self):
        cleaned = super().clean()
        ph, pd, pa = cleaned.get("p_home"), cleaned.get("p_draw"), cleaned.get("p_away")
        # If any probs provided, validate sum ~ 1.0
        provided = [v for v in (ph, pd, pa) if v is not None]
        if provided:
            if any(v < 0 or v > 1 for v in provided):
                raise forms.ValidationError("Probabilities must be between 0 and 1.")
            total = (ph or 0) + (pd or 0) + (pa or 0)
            if abs(total - 1.0) > 0.05:  # 5% tolerance
                raise forms.ValidationError("Probabilities should add up to ~1.0 (±0.05).")
        return cleaned

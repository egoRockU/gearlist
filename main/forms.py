from django.forms import ModelForm
from main.models import Review

class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ['r_cosmetics', 'r_sound', 'r_playability', 'r_build_quality', 'comment']
        labels = {
            'r_cosmetics': 'Cosmetics',
            'r_sound': 'Sound',
            'r_playability': 'Playability',
            'r_build_quality': 'Build Quality',
        }

from django import forms
from .models import Story

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = []  # 모델 필드 그대로

    # HTML에서 multiple 처리
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['images'] = forms.FileField(
            required=True,
            label='스토리 이미지',
            widget=forms.FileInput  # attrs={'multiple': True}는 templates에서 처리
        )

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='필수 입력 항목입니다.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = '150자 이하, 문자, 숫자, @/./+/-/_ 만 가능합니다.'
        self.fields['password1'].help_text = '최소 8자 이상, 숫자만으로는 불가능합니다.'
        self.fields['password2'].help_text = '확인을 위해 이전과 동일한 비밀번호를 입력하세요.'
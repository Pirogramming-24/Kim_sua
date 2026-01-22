import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.conf import settings
from .models import ChatHistory
from .decorators import login_required_with_alert
from .forms import SignUpForm



def home(request):
    return render(request, 'home.html')

# 회원가입 뷰
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'{username}님, 회원가입이 완료되었습니다!')
            login(request, user)
            return redirect('home')
    else:
        form = SignUpForm()
    
    return render(request, 'registration/signup.html', {'form': form})

# 로그인 뷰
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'{username}님, 환영합니다!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    
    return render(request, 'registration/login.html')

# 로그아웃 뷰
def logout_view(request):
    logout(request)
    messages.info(request, '로그아웃되었습니다.')
    return redirect('home')


# 공개 탭 (비로그인 허용) - 감정분석
def sentiment_view(request):
    result = None
    error = None
    history = []

    # 로그인 여부에 따라 최근 기록 불러오기
    if request.user.is_authenticated:
        history_objs = ChatHistory.objects.filter(
            user=request.user,
            model_type='sentiment'
        ).order_by('-id')[:5]
        history = [{'input': h.input_text, 'output': h.output_text} for h in history_objs]
    else:
        # 비로그인: 새로고침 시 결과 초기화
        history = []

    if request.method == 'POST':
        text = request.POST.get('text', '')

        if text:
            API_URL = "https://router.huggingface.co/hf-inference/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"
            headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"}

            response = requests.post(API_URL, headers=headers, json={
                "inputs": text,
                "options": {"wait_for_model": True}
            }, timeout=30)

            print(f"[DEBUG] Sentiment API status: {response.status_code}")
            print(f"[DEBUG] Sentiment API response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                # 일부 모델은 리스트 형태, 일부는 dict 형태
                res_list = data[0] if isinstance(data[0], list) else data
                top_sentiment = max(res_list, key=lambda x: x['score'])
                sentiment_map = {'POSITIVE': '긍정적', 'NEGATIVE': '부정적'}
                label = top_sentiment['label'].upper()
                result = f"{sentiment_map.get(label, label)} ({top_sentiment['score']:.2%})"

                if request.user.is_authenticated:
                    # 로그인 사용자는 DB에 기록
                    ChatHistory.objects.create(
                        user=request.user,
                        model_type='sentiment',
                        input_text=text,
                        output_text=result
                    )
                    # 최근 5개만 가져오기
                    history_objs = ChatHistory.objects.filter(
                        user=request.user,
                        model_type='sentiment'
                    ).order_by('-id')[:5]
                    history = [{'input': h.input_text, 'output': h.output_text} for h in history_objs]
                else:
                    # 비로그인 사용자는 결과만 바로 보여주기, session 기록은 유지하지 않음
                    history = [{'input': text, 'output': result}]

            elif response.status_code == 503:
                error = "모델 로딩 중입니다. 잠시 후 다시 시도해주세요."
            else:
                error = f"API 오류: {response.status_code} - {response.text}"
                print(f"[ERROR] Sentiment API error: {error}")

    return render(request, 'sentiment.html', {'result': result, 'error': error, 'history': history})

# 제한 탭 1 (로그인 필요) - 요약
@login_required_with_alert
def summarize_view(request):
    result = None
    error = None
    history_objs = ChatHistory.objects.filter(
        user=request.user,
        model_type='summarize'
    ).order_by('-id')[:5]
    history = [{'input': h.input_text, 'output': h.output_text} for h in history_objs]

    if request.method == 'POST':
        text = request.POST.get('text', '')

        API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"}

        response = requests.post(API_URL, headers=headers, json={
            "inputs": text,
            "parameters": {"max_length": 130, "min_length": 30},
            "options": {"wait_for_model": True}
        }, timeout=30)

        print(f"[DEBUG] Summarize API status: {response.status_code}")
        print(f"[DEBUG] Summarize API response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            result = data[0].get('summary_text', '')
            ChatHistory.objects.create(
                user=request.user,
                model_type='summarize',
                input_text=text,
                output_text=result
            )
            return redirect('summarize')
        else:
            error = f"API 오류: {response.status_code} - {response.text}"
            print(f"[ERROR] Summarize API error: {error}")

    return render(request, 'summarize.html', {'result': result, 'error': error, 'history': history})

@login_required_with_alert
def translate_view(request):
    result = None
    error = None

    # 최근 번역 기록 불러오기 (최대 5개)
    history_objs = ChatHistory.objects.filter(
        user=request.user,
        model_type='translate'
    ).order_by('-id')[:5]
    history = [{'input': h.input_text, 'output': h.output_text} for h in history_objs]

    if request.method == 'POST':
        text = request.POST.get('text', '')

        if not text:
            error = "번역할 텍스트를 입력해주세요."
        else:
            try:
                # Hugging Face Helsinki-NLP 한국어 -> 영어 모델
                API_URL = "https://router.huggingface.co/hf-inference/models/Helsinki-NLP/opus-mt-ko-en"
                headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_TOKEN}"}

                # 문장 단위로 나눠 번역 (간단하게 '.' 기준)
                sentences = [s.strip() for s in text.split('.') if s.strip()]
                translations = []

                for sentence in sentences:
                    payload = {
                        "inputs": sentence,
                        "options": {"wait_for_model": True}
                    }
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

                    # Debug 출력
                    print(f"[DEBUG] Translate API status: {response.status_code}")
                    print(f"[DEBUG] Translate API response: {response.text}")

                    if response.status_code == 200:
                        data = response.json()
                        # opus-mt-ko-en 모델 결과는 translation_text에 있음
                        translated = data[0].get('translation_text', '')
                        translations.append(translated)
                    elif response.status_code == 503:
                        error = "모델 로딩 중입니다. 잠시 후 다시 시도해주세요."
                        break
                    else:
                        error = f"API 오류: {response.status_code} - {response.text}"
                        print(f"[ERROR] Translate API error: {error}")
                        break

                # 번역 결과 합치기
                if translations and not error:
                    result = ' '.join(translations)
                    # 번역 기록 저장
                    ChatHistory.objects.create(
                        user=request.user,
                        model_type='translate',
                        input_text=text,
                        output_text=result
                    )
                    return redirect('translate')

            except Exception as e:
                error = f"번역 중 오류 발생: {str(e)}"

    return render(request, 'translate.html', {'result': result, 'error': error, 'history': history})

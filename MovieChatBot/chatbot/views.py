import os
import requests
from django.shortcuts import render
from django.http import JsonResponse
from dotenv import load_dotenv
from reviews.models import Movie, MovieReview  # MovieReview 추가

# .env 파일 로드
load_dotenv()
UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

def chatbot_view(request):
    if request.method == "POST":
        user_message = request.POST.get('message')
        
        # 1. 장르 맵 설정
        TMDB_GENRE_MAP = {
            28: "액션", 12: "모험", 16: "애니메이션", 35: "코미디", 80: "범죄",
            99: "다큐멘터리", 18: "드라마", 10751: "가족", 14: "판타지", 36: "역사",
            27: "공포", 10402: "음악", 9648: "미스터리", 10749: "로맨스", 878: "SF",
            10770: "TV 영화", 53: "스릴러", 10752: "전쟁", 37: "서부"
        }
        
        # 2. Retrieval: DB 데이터 구성 (TMDB 영화 + 사용자의 실제 리뷰)
        # (1) TMDB 영화 정보
        tmdb_movies = Movie.objects.all()
        # (2) 사용자가 직접 작성한 리뷰 정보 (RAG의 핵심!)
        my_reviews = MovieReview.objects.all()
        
        movie_context = "--- [참고할 영화 및 리뷰 목록] ---\n"
        
        # 내 리뷰 데이터 먼저 추가 (우선순위)
        for r in my_reviews:
            movie_context += (
                f"[내 리뷰] 제목: {r.title} | 평점: {r.rating}/5.0 | "
                f"내용: {r.content} | 작성일: {r.updated_at}\n"
            )

        # TMDB 영화 데이터 추가
        for m in tmdb_movies:
            raw_genre = m.genre_name if m.genre_name else ""
            genre_display = TMDB_GENRE_MAP.get(int(raw_genre), raw_genre) if raw_genre.isdigit() else (raw_genre if raw_genre else "정보 없음")
            rating_5_scale = round(m.vote_average / 2, 1) if m.vote_average else 0
            
            movie_context += (
                f"제목: {m.title} | 감독: {m.director} | 출연: {m.actors} | "
                f"장르: {genre_display} | 평점: {rating_5_scale}/5.0 | "
                f"줄거리: {m.overview[:100]}...\n"
            )

        # 3. Upstage API 호출
        url = "https://api.upstage.ai/v1/solar/chat/completions"
        headers = {
            "Authorization": f"Bearer {UPSTAGE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "solar-1-mini-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": (
                        "당신은 영화 추천 전문가 '무비봇'입니다. 제공된 [영화 및 리뷰 목록]을 바탕으로 답변하세요.\n\n"
                        "### 답변 지침 ###\n"
                        "1. [내 리뷰]라고 표시된 데이터는 사용자가 직접 작성한 경험입니다. 이를 최우선으로 참고하여 취향을 파악하세요.\n"
                        "2. 사용자가 평점을 높게 준 영화와 비슷한 장르나 배우의 영화를 [영화 목록]에서 찾아 추천하세요.\n"
                        "3. 사용자가 '내가 쓴 리뷰'나 '내가 본 영화'에 대해 물으면 정확히 답변하세요.\n"
                        "4. 말투는 영화 전문 유튜버처럼 친절하고 흥미진진하게 하세요.\n"
                        "5. 평점은 반드시 ⭐X/5.0 형태로 표현하세요.\n\n"
                        f"{movie_context}"
                    )
                },
                {"role": "user", "content": user_message}
            ]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            result = response.json()
            
            if 'choices' in result:
                reply = result['choices'][0]['message']['content']
                return JsonResponse({'status': 'success', 'reply': reply})
            else:
                return JsonResponse({'status': 'error', 'message': '응답 오류'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return render(request, 'chatbot/chat.html')
import requests
import os
from django.conf import settings
from .models import Movie

def fetch_tmdb_movies():
    # 1. API 키 가져오기 (settings.py 또는 .env 확인)
    api_key = getattr(settings, 'TMDB_API_KEY', None)
    
    # 디버깅: API 키가 비어있는지 터미널에 출력
    if not api_key:
        print("❌ 에러: TMDB_API_KEY가 설정되지 않았습니다. .env 파일이나 settings.py를 확인하세요.")
        return "API 키 설정 누락"

    # 2. TMDB API 호출 URL (인기 영화 리스트)
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=ko-KR&page=1"
    
    try:
        response = requests.get(url, timeout=5)
        
        # 🔍 터미널에서 상태 코드 확인
        print(f"📡 TMDB API 연결 시도... 상태 코드: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            movies_data = data.get('results', [])
            print(f"✅ 성공: {len(movies_data)}개의 영화 데이터를 가져왔습니다.")
            
            count = 0
            for m in movies_data:
                # --- [추가 로직: 감독 및 배우 정보 가져오기] ---
                movie_id = m['id']
                credits_url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}&language=ko-KR"
                
                director_name = "정보 없음"
                actor_names = "정보 없음"
                
                try:
                    credits_res = requests.get(credits_url, timeout=3)
                    if credits_res.status_code == 200:
                        credits_data = credits_res.json()
                        
                        # 감독(Director) 찾기
                        directors = [crew['name'] for crew in credits_data.get('crew', []) if crew['job'] == 'Director']
                        if directors:
                            director_name = directors[0]
                        
                        # 배우(Cast) 상위 3명 가져오기
                        actors = [cast['name'] for cast in credits_data.get('cast', [])[:3]]
                        if actors:
                            actor_names = ", ".join(actors)
                except Exception as e:
                    print(f"⚠️ {m['title']} 출연진 정보 가져오기 실패: {e}")
                # --------------------------------------------

                # --- [장르 ID 가져오기] ---
                genre_ids = m.get('genre_ids', [])
                target_genre = str(genre_ids[0]) if genre_ids else "기타"
                
                # 중복 방지: tmdb_id를 기준으로 저장하거나 업데이트
                movie, created = Movie.objects.update_or_create(
                    tmdb_id=movie_id,
                    defaults={
                        'title': m['title'],
                        'overview': m['overview'],
                        'release_date': m.get('release_date') or None,
                        'poster_path': m.get('poster_path'),
                        'vote_average': m.get('vote_average', 0),
                        'genre_name': target_genre,
                        'director': director_name, # 감독 저장
                        'actors': actor_names,     # 배우 저장
                    }
                )
                if created:
                    count += 1
            
            print(f"💾 결과: {count}개의 새로운 영화가 DB에 저장되었습니다.")
            return f"{count}개의 새로운 영화 저장 완료!"
        
        else:
            print(f"❌ API 호출 실패: {response.text}")
            return f"API 에러 (코드: {response.status_code})"

    except requests.exceptions.RequestException as e:
        print(f"🚀 네트워크 연결 에러 발생: {e}")
        return "네트워크 연결 오류"
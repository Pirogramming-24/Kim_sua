document.addEventListener('DOMContentLoaded', function() {
    const likeButtons = document.querySelectorAll('.btn-like');

    likeButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const postId = this.dataset.postId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            try {
                // ✅ URL을 직접 생성
                const response = await fetch(`/posts/${postId}/like/`, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': csrfToken }
                });

                if (!response.ok) throw new Error('좋아요 처리 실패');

                const data = await response.json();

                const likeCount = this.querySelector('.like-count');
                likeCount.textContent = data.likes_count;

                // 하트 색 바꾸기
                if (data.liked) this.classList.add('liked');
                else this.classList.remove('liked');

            } catch (err) {
                console.error(err);
                alert('좋아요 처리 중 오류 발생');
            }
        });
    });
});

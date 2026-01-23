document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-follow').forEach(button => {
        // 중복 이벤트 방지
        if (button.dataset.listenerAdded) return;
        button.dataset.listenerAdded = true;

        button.addEventListener('click', async () => {
            const username = button.dataset.username;
            const csrfTokenElem = document.querySelector('[name=csrfmiddlewaretoken]');
            if (!csrfTokenElem) return console.error('CSRF token not found!');
            const csrfToken = csrfTokenElem.value;

            try {
                const res = await fetch(`/accounts/follow/${username}/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({})
                });

                if (!res.ok) throw new Error('팔로우 실패');

                const data = await res.json();

                // 버튼 상태 변경
                button.textContent = data.following ? '팔로잉' : '팔로우';
                button.classList.toggle('following', data.following);

                // 팔로워 수 갱신
                const followersCount = document.getElementById('followers-count');
                if (followersCount) followersCount.textContent = data.followers_count;

            } catch (err) {
                console.error(err);
                alert('팔로우 처리 중 오류 발생');
            }
        });
    });
});

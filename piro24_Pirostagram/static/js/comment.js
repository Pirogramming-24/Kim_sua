document.addEventListener('DOMContentLoaded', function() {
    const commentForm = document.getElementById('comment-form');
    
    if (commentForm) {
        commentForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const postId = this.dataset.postId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const content = this.querySelector('[name="content"]').value;
            
            try {
                const response = await fetch(`/posts/${postId}/comment/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken,
                    },
                    body: new URLSearchParams({
                        'content': content
                    })
                });
                
                if (!response.ok) {
                    throw new Error('댓글 작성에 실패했습니다.');
                }
                
                const data = await response.json();
                
                // 댓글 리스트에 추가
                const commentsList = document.getElementById('comments-list');
                const commentHTML = `
                    <div class="comment" data-comment-id="${data.id}">
                        <div class="comment-header">
                            <strong>${data.author}</strong>
                            <div class="comment-actions">
                                <button class="btn-edit-comment" data-comment-id="${data.id}">수정</button>
                                <button class="btn-delete-comment" data-comment-id="${data.id}">삭제</button>
                            </div>
                        </div>
                        <p class="comment-text">${data.content}</p>
                        <span class="comment-date">방금 전</span>
                    </div>
                `;
                commentsList.insertAdjacentHTML('beforeend', commentHTML);
                
                // 입력 필드 초기화
                this.querySelector('[name="content"]').value = '';
                
                // 이벤트 리스너 재등록
                attachCommentEventListeners();
                
            } catch (error) {
                console.error('Error:', error);
                alert('댓글 작성 중 오류가 발생했습니다.');
            }
        });
    }
    
    function attachCommentEventListeners() {
        // 댓글 삭제
        document.querySelectorAll('.btn-delete-comment').forEach(button => {
            button.addEventListener('click', async function() {
                if (!confirm('댓글을 삭제하시겠습니까?')) return;
                
                const commentId = this.dataset.commentId;
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                try {
                    const response = await fetch(`/posts/comment/${commentId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                        },
                    });
                    
                    if (!response.ok) {
                        throw new Error('댓글 삭제에 실패했습니다.');
                    }
                    
                    // 댓글 제거
                    const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
                    commentElement.remove();
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('댓글 삭제 중 오류가 발생했습니다.');
                }
            });
        });
        
        // 댓글 수정
        document.querySelectorAll('.btn-edit-comment').forEach(button => {
            button.addEventListener('click', async function() {
                const commentId = this.dataset.commentId;
                const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
                const commentText = commentElement.querySelector('.comment-text').textContent;
                
                const newContent = prompt('댓글을 수정하세요:', commentText);
                if (!newContent || newContent === commentText) return;
                
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                
                try {
                    const response = await fetch(`/posts/comment/${commentId}/edit/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrfToken,
                        },
                        body: new URLSearchParams({
                            'content': newContent
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error('댓글 수정에 실패했습니다.');
                    }
                    
                    const data = await response.json();
                    
                    // 댓글 내용 업데이트
                    commentElement.querySelector('.comment-text').textContent = data.content;
                    
                } catch (error) {
                    console.error('Error:', error);
                    alert('댓글 수정 중 오류가 발생했습니다.');
                }
            });
        });
    }
    
    attachCommentEventListeners();
});
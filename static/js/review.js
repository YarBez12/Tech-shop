// Функция для получения CSRF-токена (если ещё не определена)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-image');
    deleteButtons.forEach(btn => {
      btn.addEventListener('click', function(e) {
        e.preventDefault();
        const imageId = btn.getAttribute('data-image-id');
        // Отправляем AJAX-запрос на удаление изображения
        fetch(`/products/review-image/${imageId}/delete/`, {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id: imageId })
        })
        .then(response => {
          if(response.ok) {
            // Удаляем контейнер с изображением
            btn.closest('.image-container').remove();
          } else {
            console.error('Deletion failed');
          }
        })
        .catch(error => console.error('Error:', error));
      });
    });
  });
  
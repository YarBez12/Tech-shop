document.addEventListener("DOMContentLoaded", function () {
    const button = document.getElementById('subscribe-btn');
    if (button) {
        button.addEventListener('click', function () {
            const brandId = button.dataset.brandId;
            const action = button.dataset.action;
            const csrftoken = getCookie('csrftoken');
            const url = button.dataset.url;

            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                },
                body: new URLSearchParams({
                    id: brandId,
                    action: action
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'ok') {
                    if (data.action === 'subscribed') {
                        button.innerText = 'Unsubscribe';
                        button.dataset.action = 'unsubscribe';
                        button.classList.remove('primary');
                        button.classList.add('red');
                    } else {
                        button.innerText = 'Subscribe';
                        button.dataset.action = 'subscribe';
                        button.classList.remove('red');
                        button.classList.add('primary');
                    }
                }
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});

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
  document.querySelectorAll('.tabular.menu a[data-tab]').forEach(tab => {
    tab.addEventListener('click', function (e) {
      e.preventDefault();
      const tabName = this.dataset.tab;
      const url = this.dataset.url;
  
      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ tab: tabName })
      }).then(() => {
        location.reload();
      });
    });
  });
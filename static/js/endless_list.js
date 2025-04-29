let page = 1;
let emptyPage = false;
let blockRequest = false;

window.addEventListener('scroll', function () {
  const margin = document.body.scrollHeight - window.innerHeight - 200;

  if (window.pageYOffset > margin && !emptyPage && !blockRequest) {
    blockRequest = true;
    page += 1;

    const params = new URLSearchParams(window.location.search);
    params.set('products_only', '1');
    params.set('page', page);

    fetch('?' + params.toString())
      .then(response => response.text())
      .then(html => {
        if (html.trim() === '') {
          emptyPage = true; 
        } else {
          const productList = document.getElementById('product-endless-list');
          productList.insertAdjacentHTML('beforeend', html);
          blockRequest = false; 
        }
      })
      .catch(error => {
        console.error('Error:', error);
        blockRequest = false;
      });
  }
});

window.dispatchEvent(new Event('scroll'));

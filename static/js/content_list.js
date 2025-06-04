const moduleOrderUrl = document.getElementById('module-list').dataset.url;

sortable('#modules', {
  forcePlaceholderSize: true,
  placeholderClass: 'placeholder'
})[0].addEventListener('sortupdate', function (e) {
  let modulesOrder = {};
  const modules = document.querySelectorAll('#modules .item');

  modules.forEach(function (module, index) {
    modulesOrder[module.dataset.id] = index;
    const orderElem = module.querySelector('.order');
    if (orderElem) {
      orderElem.innerHTML = index + 1;
    }
  });

  const options = {
    method: 'POST',
    mode: 'same-origin',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(modulesOrder)
  };

  fetch(moduleOrderUrl, options)
    .then(response => response.json())
    .then(data => location.reload())
});






const contentOrderUrl = document.getElementById('content-list').dataset.url;

sortable('#module-contents', {
  forcePlaceholderSize: true,
  placeholderClass: 'placeholder'
})[0].addEventListener('sortupdate', function (e) {
  let contentsOrder = {};
  const contents = document.querySelectorAll('#module-contents .item');

  contents.forEach(function (content, index) {
    contentsOrder[content.dataset.id] = index;
    const orderElem = content.querySelector('.order');
    if (orderElem) {
      orderElem.innerHTML = index + 1;
    }
  });

  const options = {
    method: 'POST',
    mode: 'same-origin',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(contentsOrder)
  };

  fetch(contentOrderUrl, options)
    .then(response => response.json())
    .then(data => location.reload())
});

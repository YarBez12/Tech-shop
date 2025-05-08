// var slider = document.getElementById('rangeSlider');
// var minPrice = parseFloat(slider.getAttribute('data-min-price'));
// var maxPrice = parseFloat(slider.getAttribute('data-max-price'));
// var initialMinPrice = parseFloat(slider.getAttribute('data-initial-min-price'));
// var initialMaxPrice = parseFloat(slider.getAttribute('data-initial-max-price'));
// if (!initialMinPrice) initialMinPrice = minPrice;
// if (!initialMaxPrice) initialMaxPrice = maxPrice;

// var priceFromInput = document.getElementById('price_from');
// var priceToInput = document.getElementById('price_to');

// noUiSlider.create(slider, {
//   start: [initialMinPrice, initialMaxPrice],
//   connect: true,
//   range: {
//     'min': minPrice,
//     'max': maxPrice
//   },
//   format: {
//     to: function (value) { return Math.round(value); },
//     from: function (value) { return Number(value); }
//   }
// });

// slider.noUiSlider.on('update', function (values, handle) {
//   if (handle === 0) {
//     priceFromInput.value = values[0];
//   } else {
//     priceToInput.value = values[1];
//   }
// });

// priceFromInput.addEventListener('change', function () {
//   slider.noUiSlider.set([this.value, null]);
// });
// priceToInput.addEventListener('change', function () {
//   slider.noUiSlider.set([null, this.value]);
// });



document.getElementById('sortSelector').addEventListener('change', function() {
  const selectedSort = this.value;
  const slug = this.dataset.slug;
  const url = this.dataset.url

  fetch(url, {
    method: "POST",
    headers: {
          'X-CSRFToken': getCookie('csrftoken'),
          'Content-Type': 'application/json'
    },
    body: JSON.stringify({ sort: selectedSort, slug: slug })
  }).then(() => {
    location.reload(); 
  });
});


// document.querySelector('.ui.form').addEventListener('submit', function (e) {
//   e.preventDefault();  

//   const slug = this.dataset.slug;
//   const form = e.target;
//   const formData = new FormData(form);
//   const filters = {};
//   const url = this.dataset.url

//   for (const [key, value] of formData.entries()) {
//     if (!filters[key]) {
//       filters[key] = [];
//     }
//     filters[key].push(value);
//   }

//   fetch(url, {
//     method: "POST",
//     headers: {
//       'X-CSRFToken': getCookie('csrftoken'),
//       'Content-Type': 'application/json'
//     },
//     body: JSON.stringify({ slug: slug, filters: filters })
//   }).then(() => {
//     form.submit(); 
//   });
// });



document.getElementById("applyFilters").addEventListener("click", function () {
  const form = this.closest("form");
  const slug = this.dataset.slug;
  const url = this.dataset.url;

  const formData = new FormData(form);
  const filters = {};
  for (const [key, value] of formData.entries()) {
    if (filters[key]) {
      if (Array.isArray(filters[key])) {
        filters[key].push(value);
      } else {
        filters[key] = [filters[key], value];
      }
    } else {
      filters[key] = value;
    }
  }

  filters["slug"] = slug;
  console.log(filters);

  fetch(url, {
    method: "POST",
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(filters)
  }).then(() => {
    location.reload();
  });
});

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


const slider = $("#rangeSlider");
const priceFromInput = $("#price_from");
const priceToInput = $("#price_to");

const min = parseFloat(slider.data("min-price"));
const max = parseFloat(slider.data("max-price"));
let initialMin = parseFloat(slider.data("initial-min-price")) || min;
let initialMax = parseFloat(slider.data("initial-max-price")) || max;

slider.slider({
  range: true,
  min: min,
  max: max,
  values: [initialMin, initialMax],
  slide: function (event, ui) {
    priceFromInput.val(ui.values[0]);
    priceToInput.val(ui.values[1]);
  }
});

priceFromInput.val(slider.slider("values", 0));
priceToInput.val(slider.slider("values", 1));

priceFromInput.on("change", function () {
  slider.slider("values", 0, this.value);
});

priceToInput.on("change", function () {
  slider.slider("values", 1, this.value);
});

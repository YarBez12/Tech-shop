var slider = document.getElementById('rangeSlider');
var minPrice = parseFloat(slider.getAttribute('data-min-price'));
var maxPrice = parseFloat(slider.getAttribute('data-max-price'));
var initialMinPrice = parseFloat(slider.getAttribute('data-initial-min-price'));
var initialMaxPrice = parseFloat(slider.getAttribute('data-initial-max-price'));
if (!initialMinPrice) initialMinPrice = minPrice;
if (!initialMaxPrice) initialMaxPrice = maxPrice;

var priceFromInput = document.getElementById('price_from');
var priceToInput = document.getElementById('price_to');

noUiSlider.create(slider, {
  start: [initialMinPrice, initialMaxPrice],
  connect: true,
  range: {
    'min': minPrice,
    'max': maxPrice
  },
  format: {
    to: function (value) { return Math.round(value); },
    from: function (value) { return Number(value); }
  }
});

slider.noUiSlider.on('update', function (values, handle) {
  if (handle === 0) {
    priceFromInput.value = values[0];
  } else {
    priceToInput.value = values[1];
  }
});

priceFromInput.addEventListener('change', function () {
  slider.noUiSlider.set([this.value, null]);
});
priceToInput.addEventListener('change', function () {
  slider.noUiSlider.set([null, this.value]);
});

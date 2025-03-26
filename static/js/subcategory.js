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

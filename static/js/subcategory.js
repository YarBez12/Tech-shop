$u.onReady(()=>{
  const applyBtn = document.getElementById('applyFilters');
  if (applyBtn) {
    applyBtn.addEventListener('click', async function(){
      const form = this.closest('form');
      const url = this.dataset.url;
      const slug = this.dataset.slug;

      const fd = new FormData(form);
      const filters = {};
      for (const [k,v] of fd.entries()){
        if (filters[k]) filters[k] = Array.isArray(filters[k]) ? [...filters[k], v] : [filters[k], v];
        else filters[k] = v;
      }
      filters.slug = slug;

      await $u.csrfFetch(url, { body: JSON.stringify(filters) });
      location.reload();
    });
  }

  const slider = $("#rangeSlider");
  if (slider.length){
    const priceFrom = $("#price_from");
    const priceTo = $("#price_to");
    const min = parseFloat(slider.data("min-price"));
    const max = parseFloat(slider.data("max-price"));
    const initialMin = parseFloat(slider.data("initial-min-price")) || min;
    const initialMax = parseFloat(slider.data("initial-max-price")) || max;

    slider.slider({
      range:true, min, max, values:[initialMin, initialMax],
      slide: function(_e, ui){ priceFrom.val(ui.values[0]); priceTo.val(ui.values[1]); }
    });
    priceFrom.val(slider.slider("values", 0));
    priceTo.val(slider.slider("values", 1));
    priceFrom.on("change", function(){ slider.slider("values", 0, this.value); });
    priceTo.on("change", function(){ slider.slider("values", 1, this.value); });
  }
});
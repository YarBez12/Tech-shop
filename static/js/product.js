$u.onReady(()=>{

  $('#openReviewModal').on('click', ()=> $('#reviewModal').modal('show'));
  $('#cancelReview').on('click', ()=> $('#reviewModal').modal('hide'));

  (function(){
    const dd = $('#ratingFilter');
    if (!dd.length) return;
    let initializing = true;
    dd.dropdown({
      onChange: async function(value){
        if (initializing) return;
        const url = this.dataset.url;
        const slug = this.dataset.slug;
        await $u.csrfFetch(url, { body: JSON.stringify({ rating: value==='all' ? null : parseInt(value), slug }) });
        location.reload();
      }
    });
    const cur = dd.data('selected');
    dd.dropdown('set selected', cur ? String(cur) : 'all');
    initializing = false;
  })();

  (function(){
    const main = $('#mainProductImage');
    if (!main.length) return;

    const images = [];
    images.push(main.attr('src'));
    $('.preview-image').each(function(){ images.push($(this).attr('src')); });

    let current = 0;
    const modal = $('#imagePreviewModal');
    const img = $('#modalPreviewImage');

    function updateThumbs(){
      $('.modal-thumbnails img').css('border-color','transparent');
      $(`.modal-thumbnails img[data-index="${current}"]`).css('border-color','#2185d0');
    }
    function open(index){
      current = index;
      img.attr('src', images[current]);
      const box = $('.modal-thumbnails').empty();
      images.forEach((src, i)=>{
        const t = $('<img>').attr({src, 'data-index': i}).css({width:'60px', cursor:'pointer', border:'2px solid transparent', 'border-radius':'4px'});
        box.append(t);
      });
      updateThumbs();
      modal.modal('show');
    }

    $('#mainProductImage, .preview-image').on('click', function(){
      open(parseInt($(this).data('index')));
    });

    $('.nav-arrow.left').on('click', function(e){
      e.stopPropagation();
      current = (current - 1 + images.length) % images.length;
      img.attr('src', images[current]); updateThumbs();
    });
    $('.nav-arrow.right').on('click', function(e){
      e.stopPropagation();
      current = (current + 1) % images.length;
      img.attr('src', images[current]); updateThumbs();
    });
    $('.modal-thumbnails').on('click', 'img', function(){
      current = parseInt($(this).attr('data-index')); img.attr('src', images[current]); updateThumbs();
    });
  })();

  $u.delegate(document, '.custom-tag', 'click', async (e, el)=>{
    const url = el.dataset.url;
    try {
      const html = await (await fetch(url)).text();
      $('#tag-modal').remove();
      $('body').append(html);
      $('#tag-modal').modal('show');
    } catch { alert('Error while loading products with this tag'); }
  });

  document.querySelectorAll('[id^="review-gallery-"]').forEach(g=>{
    lightGallery(g, { selector:'a', plugins:[lgZoom, lgThumbnail], speed:400 });
  });

  $u.qsa('[data-tab-name]').forEach(tab=>{
    tab.addEventListener('click', async (e)=>{
      e.preventDefault();
      const url = tab.dataset.url;
      const slug = tab.dataset.slug;
      const name = tab.dataset.tabName;
      await $u.csrfFetch(url, { body: JSON.stringify({ tab: name, slug }) });
      location.reload();
    });
  });
});
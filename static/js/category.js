$u.onReady(()=>{
  $u.delegate(document, '.ui.card[data-url]', 'click', async (e, card)=>{
    const url = card.dataset.url;
    try {
      const html = await (await fetch(url)).text();
      $('.ui.modal').remove();
      $('body').append(html);
      $('.ui.modal').modal('show');
    } catch {
      alert('Error while loading subcategory details');
    }
  });
});
  
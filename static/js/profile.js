$u.onReady(()=>{
  $('#open-product-modal').on('click', ()=> $('#product-modal').modal('show'));
  $('#cancel-product').on('click', ()=> $('#product-modal').modal('hide'));
});
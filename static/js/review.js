$u.onReady(()=>{
  $u.delegate(document, '.delete-image', 'click', async (e, btn)=>{
    e.preventDefault();
    const imageId = btn.dataset.imageId;
    const url = `/products/review-image/${imageId}/delete/`;
    const res = await $u.csrfFetch(url, { body: JSON.stringify({ id: imageId }) });
    if (res.ok) btn.closest('.image-container')?.remove();
    else console.error('Deletion failed');
  });

  const g = document.querySelector('#review-edit-gallery');
  if (g) lightGallery(g, { selector:'a', plugins:[lgZoom, lgThumbnail], speed:400 });
});
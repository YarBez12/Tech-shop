$u.onReady(()=>{
  const g = document.querySelector('#review-edit-gallery');
  if (g) lightGallery(g, { selector:'a', plugins:[lgZoom, lgThumbnail], speed:400 });
});
function initSortable(listSel, urlDataId){
  const list = document.getElementById(urlDataId);
  if (!list) return;
  const url = list.dataset.url;

  const s = sortable(listSel, { forcePlaceholderSize:true, placeholderClass:'placeholder' })[0];
  s.addEventListener('sortupdate', ()=>{
    const payload = {};
    document.querySelectorAll(`${listSel} .item`).forEach((el, i)=>{
      payload[el.dataset.id] = i;
      const order = el.querySelector('.order');
      if (order) order.textContent = i + 1;
    });
    fetch(url, {
      method:'POST',
      headers:{ 'Content-Type':'application/json' },
      body: JSON.stringify(payload)
    }).then(r=>r.json()).then(()=>location.reload());
  });
}

$u.onReady(()=>{
  initSortable('#modules', 'module-list');
  initSortable('#module-contents', 'content-list');
});
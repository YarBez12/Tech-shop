$u.onReady(()=>{
  const container = document.getElementById('product-endless-list');
  if (!container) return;

  let page = 1, empty = false, loading = false;
  const sentinel = document.createElement('div');
  sentinel.id = 'endless-sentinel';
  container.after(sentinel);

  const loadMore = async ()=>{
    if (empty || loading) return;
    loading = true;
    const params = new URLSearchParams(location.search);
    params.set('products_only','1');
    params.set('page', String(++page));
    const html = await (await fetch(`?${params.toString()}`)).text();
    if (html.trim()==='') empty = true;
    else container.insertAdjacentHTML('beforeend', html);
    loading = false;
  };

  const io = new IntersectionObserver((entries)=>{
    if (entries.some(e=>e.isIntersecting)) loadMore();
  }, {rootMargin:'200px'});
  io.observe(sentinel);
});
$u.onReady(()=>{
  const input = document.getElementById('search-input');
  const box = document.getElementById('search-suggestions');
  const btn = document.getElementById('search-btn');
  const urlEl = document.getElementById('search-suggestions-url');
  if (!input || !box || !btn || !urlEl) return;
  const searchUrl = urlEl.value;

  let t = null;
  const debounce = (fn, ms)=>{
  let t;
  return function(...args){
    const ctx = this;
    clearTimeout(t);
    t = setTimeout(()=> fn.apply(ctx, args), ms);
  };
};

  async function fetchSuggestions(q){
    const res = await fetch(`${searchUrl}?q=${encodeURIComponent(q)}`);
    return res.json();
  }

  input.addEventListener('input', debounce(async function(){
    const q = this.value.trim();
    if (!q) { box.style.display='none'; box.innerHTML=''; return; }

    const data = await fetchSuggestions(q);
    box.innerHTML='';
    const total = data.categories.length + data.products.length;
    if (!total) { box.style.display='none'; return; }

    box.style.display='block';
    const addItem = (title, href)=>{
      const li = document.createElement('li');
      li.className = 'list-group-item';
      li.innerHTML = `<strong>${title}</strong>`;
      li.addEventListener('click', ()=> window.location.href = href);
      box.appendChild(li);
    };
    data.categories.forEach(c=> addItem(c.title, c.url));
    data.products.forEach(p=> addItem(p.title, p.url));
  }, 200));

  document.addEventListener('click', (e)=>{
    if (!input.contains(e.target) && !box.contains(e.target)) box.style.display='none';
  });

  input.addEventListener('keypress', (e)=>{ if (e.key==='Enter') btn.click(); });
});
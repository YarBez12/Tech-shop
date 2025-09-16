$u.onReady(()=>{
  const btn = document.getElementById('subscribe-btn');
  if (!btn) return;

  btn.addEventListener('click', async ()=>{
    const url = btn.dataset.url;
    const body = new URLSearchParams({ id: btn.dataset.brandId, action: btn.dataset.action });

    const res = await fetch(url, { method:'POST', headers: $u.csrfHeaders(), body });
    const data = await res.json();

    if (data.status === 'ok') {
      const subscribed = data.action === 'subscribed';
      btn.innerText = subscribed ? 'Unsubscribe' : 'Subscribe';
      btn.dataset.action = subscribed ? 'unsubscribe' : 'subscribe';
      btn.classList.toggle('primary', !subscribed);
      btn.classList.toggle('red', subscribed);
    }
  });
});
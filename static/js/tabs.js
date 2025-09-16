$u.onReady(()=>{
  $u.qsa('.tabular.menu a[data-tab]').forEach(a=>{
    a.addEventListener('click', async (e)=>{
      e.preventDefault();
      const url = a.dataset.url;
      if (!url) return;
      await $u.csrfFetch(url, { body: JSON.stringify({ tab: a.dataset.tab }) });
      location.reload();
    });
  });
});
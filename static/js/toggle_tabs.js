$u.onReady(()=>{
  $u.delegate(document, '.tab-button', 'click', (e, btn)=>{
    e.preventDefault();
    document.querySelectorAll('.tab-button.active').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.tab-panel.active').forEach(p=>p.classList.remove('active'));
    btn.classList.add('active');
    const id = btn.dataset.tab;
    const panel = document.getElementById(id);
    if (panel) panel.classList.add('active');
  });
});
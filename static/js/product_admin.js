$u.onReady(()=>{
  const cat = document.getElementById('id_category');
  const addBtn = document.querySelector('.add-row a');
  if (!cat || !addBtn) return;

  cat.addEventListener('change', async function(){
    const categoryId = this.value;
    const rows = document.querySelectorAll('.dynamic-productcharacteristic_set');
    rows.forEach(r=>r.remove());

    if (!categoryId) return;

    const data = await (await fetch(`/admin/get_characteristics/?category_id=${categoryId}`)).json();
    data.characteristics.forEach(ch=>{
      addBtn.click();
      const last = document.querySelector('.dynamic-productcharacteristic_set:last-child');
      const cField = last?.querySelector('select[name$="-characteristic"]');
      const vField = last?.querySelector('input[name$="-value"]');
      if (cField) cField.value = ch.id;
      if (vField) vField.value = '';
    });
  });
});
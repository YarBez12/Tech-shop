$u.onReady(()=>{
  const ch = document.getElementById('show-address');
  const box = document.getElementById('address-section');
  const form = document.querySelector('form');
  if (!ch || !box || !form) return;

  const alwaysOptional = new Set(['id_address_field1','id_address_field2','id_state']);

  function toggle(){
    const inputs = box.querySelectorAll('input, select, textarea');
    if (ch.checked){
      box.classList.remove('hidden');
      inputs.forEach(i=>{
        i.removeAttribute('disabled');
        if (!alwaysOptional.has(i.id)) i.setAttribute('required','required');
        else i.removeAttribute('required');
      });
    } else {
      box.classList.add('hidden');
      inputs.forEach(i=>{
        i.removeAttribute('required');
        i.setAttribute('disabled', true);
      });
    }
  }

  ch.addEventListener('change', toggle);
  form.addEventListener('submit', toggle);
  toggle();
});
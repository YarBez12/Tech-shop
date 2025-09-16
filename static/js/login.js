$u.onReady(()=>{
  $('.ui.checkbox').checkbox();

  const icon = $('#toggle-password');
  const label = $('#toggle-label');
  const pass = $('#id_password');
  if (!icon.length || !label.length || !pass.length) return;

  function toggle(){
    const type = pass.attr('type') === 'password' ? 'text' : 'password';
    pass.attr('type', type);
    icon.toggleClass('eye').toggleClass('eye slash');
    label.text(type === 'password' ? 'Show password' : 'Hide password');
  }
  icon.on('click', toggle);
  label.on('click', toggle);
});
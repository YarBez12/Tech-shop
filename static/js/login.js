$('.ui.checkbox').checkbox();

  $('#toggle-password, #toggle-label').on('click', function () {
    const passwordField = $('#id_password');
    const type = passwordField.attr('type') === 'password' ? 'text' : 'password';
    passwordField.attr('type', type);
    
    const icon = $('#toggle-password');
    icon.toggleClass('eye').toggleClass('eye slash');

    $('#toggle-label').text(type === 'password' ? 'Show password' : 'Hide password');
  });
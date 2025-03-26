$(document).ready(function () {
    $('.ui.message .close').on('click', function () {
      $(this).closest('.message').transition('fade');
    });
    $('.ui.dropdown.simple').dropdown({ on: 'click' });
    $('.ui.dropdown.category').dropdown({ on: 'hover' });
  });


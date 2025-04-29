$(document).ready(function () {
    $('.ui.message .close').on('click', function () {
      $(this).closest('.message').transition('fade');
    });
    $('.ui.dropdown.simple').dropdown({ on: 'click' });
    $('.ui.dropdown.category').dropdown({ on: 'hover' });
  });

  document.addEventListener("DOMContentLoaded", function () {
    $('#mobile-menu-toggle').on('click', function () {
      $('.ui.sidebar')
        .sidebar('setting', 'transition', 'overlay')
        .sidebar('toggle');
    });
  });
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.order-header').forEach(function(header) {
      header.addEventListener('click', function() {
        var details = this.nextElementSibling;
        if(details.style.display === 'none' || details.style.display === '') {
          details.style.display = 'block';
        } else {
          details.style.display = 'none';
        }
      });
    });
  });
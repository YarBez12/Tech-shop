$(document).ready(function () {
    $('.ui.card').on('click', function () {
      const subcategorySlug = $(this).data('subcategory-slug');
      const url = $(this).data('url');
  
      $.ajax({
        url: url,
        method: 'GET',
        success: function (html) {
          $('.ui.modal').remove();
            $('body').append(html);
            $('.ui.modal').modal('show');
        },
        error: function () {
          alert('Error while loading subcategory details');
        }
      });
    });
  });
  
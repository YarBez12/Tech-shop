$(document).ready(function () {
    $('.ui.card').on('click', function () {
      const subcategorySlug = $(this).data('subcategory-slug');
      const url = $(this).data('url');
  
      $.ajax({
        url: url,
        method: 'GET',
        success: function (html) {
          // Удалим предыдущую модалку (если была)
          $('.ui.modal').remove();
  
          // Добавим новую модалку в body
          $('body').append(html);
  
          // И откроем её
          $('.ui.modal').modal('show');
        },
        error: function () {
          alert('Ошибка при загрузке данных подкатегории');
        }
      });
    });
  });
  
// Переключение вкладок
  
  // // Функции для модального окна
  // function openModal(src) {
  //   document.getElementById('modalImage').src = src;
  //   document.getElementById('photoModal').style.display = 'block';
  // }
  // function closeModal() {
  //   document.getElementById('photoModal').style.display = 'none';
  // }
  // function selectPhoto(src) {
  //   document.getElementById('modalImage').src = src;
  // }
  // function prevPhoto() {
  //   // Реализуйте логику перехода к предыдущей фотографии
  // }
  // function nextPhoto() {
  //   // Реализуйте логику перехода к следующей фотографии
  // }
  // document.getElementById('photoModal').addEventListener('click', function(e) {
  //   if (e.target === this) {
  //     closeModal();
  //   }
  // });

  $('#openReviewModal').on('click', function () {
    $('#reviewModal').modal('show');
  });
  
  $('#cancelReview').on('click', function () {
    $('#reviewModal').modal('hide');
  });

  let initializing = true; 
  $('#ratingFilter').dropdown({
    onChange: function (value, text, $choice) {
      if (initializing) return;
      const params = new URLSearchParams(window.location.search);

      if (value === 'all') {
        params.delete('rating');
      } else {
        params.set('rating', value);
      }

      window.location.search = params.toString();
    }
  });

  const currentRating = new URLSearchParams(window.location.search).get('rating');
  if (currentRating) {
    $('#ratingFilter').dropdown('set selected', currentRating);
  } else {
    $('#ratingFilter').dropdown('set selected', 'all');
  }
  initializing = false;

    
  


    var images = [];
    
    var mainImage = $('#mainProductImage');
    images.push(mainImage.attr('src'));
    
    $('.preview-image').each(function(){
      images.push( $(this).attr('src'));
    });
    
    $('#mainProductImage, .preview-image').on('click', function(){
      var index = parseInt($(this).data('index'));
      openImageModal(index);
    });
    
    var currentIndex = 0;
    
    function openImageModal(index) {
      currentIndex = index;
      $('#modalPreviewImage').attr('src', images[currentIndex]);
      
      var thumbContainer = $('.modal-thumbnails');
      thumbContainer.empty();
      images.forEach(function(image, idx){
        var thumb = $('<img>')
          .attr('src', image)
          .attr('data-index', idx)
          .css({
            'width': '60px',
            'cursor': 'pointer',
            'border': '2px solid transparent',
            'border-radius': '4px'
          });
        if(idx === currentIndex){
          thumb.css('border-color', '#2185d0');
        }
        thumbContainer.append(thumb);
      });
      
      $('#imagePreviewModal').modal('show');
    }
    
    $('.nav-arrow.left').on('click', function(e){
      e.stopPropagation();
      currentIndex = (currentIndex - 1 + images.length) % images.length;
      $('#modalPreviewImage').attr('src', images[currentIndex]);
      updateModalThumbnails();
    });
    
    $('.nav-arrow.right').on('click', function(e){
      e.stopPropagation();
      currentIndex = (currentIndex + 1) % images.length;
      $('#modalPreviewImage').attr('src', images[currentIndex]);
      updateModalThumbnails();
    });
    
    $('.modal-thumbnails').on('click', 'img', function(){
      currentIndex = parseInt($(this).attr('data-index'));
      $('#modalPreviewImage').attr('src', images[currentIndex]);
      updateModalThumbnails();
    });
    
    function updateModalThumbnails(){
      $('.modal-thumbnails img').css('border-color', 'transparent');
      $('.modal-thumbnails img[data-index="'+currentIndex+'"]').css('border-color', '#2185d0');
    }

  
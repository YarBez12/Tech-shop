// Переключение вкладок
  
  // Функции для модального окна
  function openModal(src) {
    document.getElementById('modalImage').src = src;
    document.getElementById('photoModal').style.display = 'block';
  }
  function closeModal() {
    document.getElementById('photoModal').style.display = 'none';
  }
  function selectPhoto(src) {
    document.getElementById('modalImage').src = src;
  }
  function prevPhoto() {
    // Реализуйте логику перехода к предыдущей фотографии
  }
  function nextPhoto() {
    // Реализуйте логику перехода к следующей фотографии
  }
  document.getElementById('photoModal').addEventListener('click', function(e) {
    if (e.target === this) {
      closeModal();
    }
  });

  document.querySelector('.add-review').addEventListener('click', function() {
    var container = document.getElementById('reviewFormContainer');
    if (container.style.display === 'none' || container.style.display === '') {
      container.style.display = 'block';
    } else {
      container.style.display = 'none';
    }
  });
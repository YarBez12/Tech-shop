$(".carousel-inner").slick({
    dots: false,
    infinite: true,
    speed: 500,
    slidesToShow: 1,
    adaptiveHeight: true,
    nextArrow:
      '<button type="button" class="ui icon button slick-next"><i class="angle right icon"></i></button>',
    prevArrow:
      '<button type="button" class="ui icon button slick-prev"><i class="angle left icon"></i></button>',
  });
  $(".ui.checkbox").checkbox();
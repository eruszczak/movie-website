$(document).ready(function() {
    var $slickCarousel = $('.slick-carousel');
    if ($slickCarousel) {
        $slickCarousel.on('init', function(event, slick) {
            // on init, show card of first carousel item. it is hidden on init load to avoid weird `flickering`
            $('.slick-slide.slick-current.slick-active').find('.card1').first().fadeIn();
        });

        $slickCarousel.slick({
          // 'centerMode': true,
          'dots': true,
          lazyLoad: 'ondemand',
          // 'dotsClass': '',
          // 'mobileFirst': true,
          // 'respondTo': 'slider'  // window, slider min,
          // 'responsive': ''
        });

        $slickCarousel.on('beforeChange', function(event, slick, currentSlide, nextSlide) {
            $("[data-slick-index='" + nextSlide + "']").find('.slick-item').first().css('visibility', 'visible');
            // $('.slick-slide.slick-current.slick-active').find('.still-background').first().css('visibility', 'visible');
        });
    }

    var $slickCarouselSimilar = $('.slick-carousel-similar');
    if ($slickCarouselSimilar) {
        $slickCarouselSimilar.slick({
            infinite: false,
            lazyLoad: 'ondemand',
            slidesToShow: 7,
            responsive: [
                {
                    breakpoint: 1024,
                    settings: {
                        slidesToShow: 4,
                        // infinite: true
                    }
                },
                {
                    breakpoint: 800,
                    settings: {
                        slidesToShow: 3,
                        // dots: true
                    }
                },
                {
                    breakpoint: 600,
                    settings: {
                        slidesToShow: 2,
                        // dots: true
                    }
                },
                // {
                //     breakpoint: 300,
                //     settings: "unslick" // destroys slick
                // }
            ]
        }).on('beforeChange', function(event, slick, currentSlide, nextSlide) {
            $("[data-slick-index='" + nextSlide + "']").find('.slick-item').first().css('visibility', 'visible');
        }).on('lazyLoaded', function(event, slick, image, imageSource){
            // console.log($(image));
            // $('[type="tooltip"]').popup();
        });
    }
});

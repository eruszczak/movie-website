$(document).ready(function() {
    var $slickCarousel = $('.slick-carousel');
    if ($slickCarousel) {
        $slickCarousel.slick({
          'dots': true,
          lazyLoad: 'ondemand',
          responsive: [
            {
                breakpoint: 600,
                settings: {
                    dots: false
                }
            }
        ]
        }).on('beforeChange', function(event, slick, currentSlide, nextSlide) {
            $("[data-slick-index='" + nextSlide + "']").find('.slick-item').first().css('visibility', 'visible');
        }).on('lazyLoaded', function(event, slick, image, imageSource){
            $(image).parent().find('[type="tooltip"]').popup();
        });
    }

    var $slickCarouselSmall = $('.slick-carousel-small');
    if ($slickCarouselSmall) {
        $slickCarouselSmall.slick({
            infinite: false,
            lazyLoad: 'ondemand',
            slidesToShow: 7,
            dots: true,
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
                        dots: false
                    }
                },
            ]
        }).on('beforeChange', function(event, slick, currentSlide, nextSlide) {
            $("[data-slick-index='" + nextSlide + "']").find('.slick-item').first().css('visibility', 'visible');
        }).on('lazyLoaded', function(event, slick, image, imageSource){
            $(image).parent().parent().popup();
        });
    }
});

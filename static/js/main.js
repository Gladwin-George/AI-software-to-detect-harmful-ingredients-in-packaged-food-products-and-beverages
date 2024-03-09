$(document).ready(function(){
   
    $("form").on("submit", function(event){
        event.preventDefault();
        
                var formData = new FormData(this);
        
                $.ajax({
                    url: '/',
                    type: 'POST',
                    data: formData,
                    success: function(data){
                        // Clear any existing error message and harmful ingredients
                        $('.error').text('');
                        $('#harmful-ingredients-list').empty();
        
                        // Display the error message, if any
                        if (data.error) {
                            $('.error').text(data.error);
                        }
        
                        // Display the harmful ingredients, if any
                        if (data.harmful_ingredients.length > 0) {
                            $.each(data.harmful_ingredients, function(i, ingredient) {
                                $('#harmful-ingredients-list').append('<li>' + ingredient[0] + ' - ' + ingredient[1] + '</li>');
                            });
                        }
                    },
                    cache: false,
                    contentType: false,
                    processData: false
                });
    });

    // Add smooth scrolling to all links
    $("a").on('click', function(event) {
        // Make sure this.hash has a value before overriding default behavior
        if (this.hash !== "") {
            // Prevent default anchor click behavior
            event.preventDefault();

            // Store hash
            var hash = this.hash;

            // Using jQuery's animate() method to add smooth page scroll
            // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800, function(){
        
            // Add hash (#) to URL when done scrolling (default click behavior)
            window.location.hash = hash;
            });
        } // End if
    });

    var swiper = new Swiper(".mySwiper", {
        slidesPerView: 3,
        spaceBetween: 30,
        autoplay: {
            delay: 2500,
            disableOnInteraction: false,
        },
        pagination: {
          el: ".swiper-pagination",
          clickable: true,
        },
    });

});

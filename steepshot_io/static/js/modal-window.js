/*script for modal window*/

$('#modal_close, #overlay').click( function(){
    $('#modal_form').animate({opacity: 0, top: '45%'}, 200,
            function(){
                $(this).css('display', 'none');
                $('#overlay').fadeOut(400);
            }
        );
});

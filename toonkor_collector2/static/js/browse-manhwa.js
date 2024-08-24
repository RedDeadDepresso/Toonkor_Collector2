$(document).ready(function() {

    function updateLibrary(actionUrl, currentButton, newButtonId, newButtonText, removeClass, addClass) {
        var slug = currentButton.attr("value");
        console.log(slug);
        $.ajax({
            url: actionUrl,
            type: 'GET',
            contentType: 'application/json',
            data: { 'slug': slug },
            success: function(response) {
                if (response.status === "success") {
                    currentButton.attr('id', newButtonId)
                                 .text(newButtonText)
                                 .removeClass(removeClass)
                                 .addClass(addClass);
                }
            }
        });
    }

    $(document).on('click', '#add_library', function() {
        updateLibrary(
            '/toonkor_collector2/add_library/',
            $(this),
            'remove_library',
            'Remove from Library',
            'btn-primary',
            'btn-danger'
        );
    });

    $(document).on('click', '#remove_library', function() {
        updateLibrary(
            '/toonkor_collector2/remove_library/',
            $(this),
            'add_library',
            'Add to Library',
            'btn-danger',
            'btn-primary'
        );
    });

});

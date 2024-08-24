$(document).ready(function() {
    // Handle select all checkboxes
    $(document).on('click', '#select_all', function() {
        $('.chapter-checkbox').prop('checked', true);
    });

    // Handle clear all checkboxes
    $(document).on('click', '#clear_all', function() {
        $('.chapter-checkbox').prop('checked', false);
    });

    // Handle download button click
    $(document).on('click', '#download_button', function() {
        // Get the value of the slug
        var slug = $('#remove_library').val();
        var chapters = [];
        
        // Collect all checked checkboxes
        $('.chapter-checkbox:checked').each(function() {
            chapters.push($(this).val());
        });
        console.log(chapters);

        // Send AJAX request to download the selected chapters
        $.ajax({
            url: '/toonkor_collector2/download/' + slug,
            method: 'GET',
            data: {'chapters': chapters},
            traditional: true, // ensures array is serialized as `chapters[]=value1&chapters[]=value2`
            success: function(response) {
                console.log(response.status);
            },
            error: function(error) {
                console.error("Error starting download:", error);
            }
        });
    });
});

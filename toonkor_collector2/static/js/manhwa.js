$(document).ready(function() {
    $(document).on('click', '#add_library', function() {
        var slug = $('#add_library').attr("value");
        $.ajax({
            url: '/toonkor_collector2/add_library/',
            type: 'GET',
            contentType: 'application/json',
            data: { 'slug': slug },
            success: function(response) {
                if (response.status === "success") {
                    console.log(response.redirect)
                    window.location.replace(response.redirect);
                }
            }
        })
    });

    $(document).on('click', '#remove_library', function() {
        var slug = $('#remove_library').attr("value");
        $.ajax({
            url: '/toonkor_collector2/remove_library/',
            type: 'GET',
            contentType: 'application/json',
            data: { 'slug': slug },
            success: function(response) {
                if (response.status === "success") {
                    console.log(response.redirect)
                    window.location.replace(response.redirect);
                }
            }
        });
    });

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

        const downloadSocket = new WebSocket('ws://' + window.location.host + '/ws/download/');
        
        downloadSocket.onopen = function() {
            // Send data when WebSocket connection is open
            downloadSocket.send(JSON.stringify(
                { slug: slug, chapters: chapters }
            ));
        };
    
        downloadSocket.onmessage = function(e) {
            var data = JSON.parse(e.data);
            var progress = Math.floor(data.current / data.total * 100);
            $('.progress-block').css('display', 'block');
            $('.progress-bar').css('width', progress + '%');
            $('.progress-bar').text(progress + '%');
            $('#progress-text').text(`${data.current}/${data.total}`);
            if (progress === 100) {
                $('#progress-status').text('Status: Download Completed');
                downloadSocket.close(); // Close the WebSocket when download is complete
            }
            else {
                $('#progress-status').text('Status: Downloading');
            }
        };
    
        downloadSocket.onerror = function(e) {
            console.error('WebSocket error:', e);
        };
    
        downloadSocket.onclose = function(e) {
            if (e.wasClean) {
                console.log('WebSocket closed cleanly');
            } else {
                console.error('WebSocket closed unexpectedly:', e);
            }
        };
    })
});
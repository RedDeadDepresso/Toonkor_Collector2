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
        const downloadSocket = new WebSocket('ws://' + window.location.host + '/ws/download_translate/' + slug + '/');
        
        downloadSocket.onopen = function() {
            // Send data when WebSocket connection is open
            downloadSocket.send(JSON.stringify(
                { slug: slug, chapters: chapters, task: 'download' }
            ));
        };
    
        downloadSocket.onmessage = function(e) {
            var data = JSON.parse(e.data).progress;
            var progress = Math.floor(data.current / data.total * 100);
            $('#download-block').css('display', 'block');
            $('#download-bar').css('width', progress + '%');
            $('#download-bar').text(progress + '%');
            $('#download-counter').text(`${data.current}/${data.total}`);
            if (progress === 100) {
                $('#download-status').text('Status: Download Completed');
            }
            else {
                $('#download-status').text('Status: Downloading');
                downloadSocket.close(); // Close the WebSocket when download is complete
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

    // Handle download button click
    $(document).on('click', '#download_translate_button', function() {
        // Get the value of the slug
        var slug = $('#remove_library').val();
        var chapters = [];
        
        // Collect all checked checkboxes
        $('.chapter-checkbox:checked').each(function() {
            chapters.push($(this).val());
        });
        const downloadSocket = new WebSocket('ws://' + window.location.host + '/ws/download_translate/' + slug);
        
        downloadSocket.onopen = function() {
            // Send data when WebSocket connection is open
            downloadSocket.send(JSON.stringify(
                { slug: slug, chapters: chapters, task: 'download_translate' }
            ));
        };
    
        downloadSocket.onmessage = function(e) {
            var data = JSON.parse(e.data).progress;
            var progress = Math.floor(data.current / data.total * 100);
            if (data.task === 'download') {
                $('#download-block').css('display', 'block');
                $('#download-bar').css('width', progress + '%');
                $('#download-bar').text(progress + '%');
                $('#download-counter').text(`${data.current}/${data.total}`);
                if (progress === 100) {
                    $('#download-status').text('Status: Download Completed');
                }
                else {
                    $('#download-status').text('Status: Downloading');
                }
            }
            else {
                $('#translate-block').css('display', 'block');
                $('#translate-bar').css('width', progress + '%');
                $('#translate-bar').text(progress + '%');
                $('#translate-counter').text(`${data.current}/${data.total}`);
                if (progress === 100) {
                    $('#translate-status').text('Status: Translation Completed');
                    downloadSocket.close(); // Close the WebSocket when download is complete
                }
                else {
                    $('#translate-status').text('Status: Translating')
                }
            }
        }
    
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
    }
)})
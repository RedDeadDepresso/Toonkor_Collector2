$(document).ready(function() {
    $('#search').on('keydown', function(event) {
        if (event.keyCode === 13) { // 13 is the Enter key code
            event.preventDefault(); // Prevent the default action (form submission, etc.)
            reactSearch(); // Call your function
        }
    });
    
    function updateTextBlock(string) {
        $('#text-block').text(string);
    }

    function generateCard(manhwa) {
        var cardHtml = `
            <div class="col">
                <div class="card h-100">
                    <img src="${manhwa.thumbnail_url}" class="card-img-top" alt="${manhwa.title} banner">
                    <div class="card-body">
                        <h5 class="card-title">${manhwa.title}</h5>
                    </div>
                </div>
            </div>
        `;
        $('#manhwa-block').append(cardHtml);
    }

    function reactSearch() {
        var query = $('#search').val();
        $.ajax({
            url: '/toonkor_collector2/browse_search/',
            type: 'GET',
            data: {
                'query': query
            },
            dataType: "json",

            success: function(response) {
                $('#manhwa-block').empty();
                if (response.results.length === 0) {
                    updateTextBlock('No results were found.');
                }
                else {
                    updateTextBlock('');
                    response.results.forEach(manhwa => {generateCard(manhwa)});
                }
            },
        })
    }
});

$(document).ready(function() {
    let typingTimer;                // Timer identifier
    let typingDelay = 1000;         // Delay in milliseconds (2 seconds)
    let searchInput = $('#search'); // Input element

    // On keyup, start the countdown
    searchInput.on('keyup', function() {
        clearTimeout(typingTimer);  // Clear the previous timer
        typingTimer = setTimeout(doneTyping, typingDelay); // Start a new timer
    });

    // On keydown, clear the timer (if the user is typing)
    searchInput.on('keydown', function() {
        clearTimeout(typingTimer); // Reset the timer if the user presses another key
    });

    // User is "finished typing," do something
    function doneTyping() {
        let query = searchInput.val();
        reactSearch(query); // Call your function, e.g., reactSearch(query)
    }

    searchInput.on('keydown', function(event) {
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

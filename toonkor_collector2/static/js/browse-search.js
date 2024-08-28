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

    function getCookie(cname) {
        let name = cname + "=";
        let decodedCookie = decodeURIComponent(document.cookie);
        let ca = decodedCookie.split(';');
        for(let i = 0; i <ca.length; i++) {
          let c = ca[i];
          while (c.charAt(0) == ' ') {
            c = c.substring(1);
          }
          if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
          }
        }
        return "";
      }

    function generateCard(manhwa) {
        var title = getCookie('display_english') === "true" ? manhwa.en_title : manhwa.title;
        var cardHtml = `
            <div class="col">
                <div class="card h-100">
                    <img src="${manhwa.thumbnail_url}" class="card-img-top" alt="${title} thumbnail">
                    <div class="card-body">
                        <a class="link-title stretched-link" href="/toonkor_collector2/browse_manhwa${manhwa.url}/">
                        <h5 class="card-title">${title}</h5>
                        </a>
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

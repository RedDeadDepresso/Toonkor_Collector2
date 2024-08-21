$(document).ready(function() { 
    var theme = $('html').attr('data-bs-theme');
    if (theme == 'dark') {
        $("#theme-switch").prop("checked", true);
    };

    $('#theme-switch').change(function() {
        $.get('/toonkor_collector2/theme/',
        {'theme': newTheme})
        $('html').attr('data-bs-theme', newTheme); 
    });
});

$(document).ready(function() { 
    $('#id_username,#id_password,#id_email,#id_password1,#id_password2').addClass('form-control');

    var theme = $('html').attr('data-bs-theme');
    if (theme == 'dark') {
        $("#theme-switch").prop("checked", true);
    };

    $('#theme-switch').change(function() {
        if ($(this).is(":checked")) {
            var newTheme = 'dark';  
            $('#id_animal,#id_animals').select2({
                theme: "bootstrap5-dark"
            });
        }
        else {
            var newTheme = 'light';
            $('#id_animal,#id_animals').select2({
                theme: "bootstrap5"
            });
        }

        $.get('/wildthoughts/theme/',
        {'theme': newTheme})
        $('html').attr('data-bs-theme', newTheme); 
    });
});

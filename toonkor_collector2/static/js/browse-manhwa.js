$(document).ready(function(){
    $(document).on('click', '#add_library', function(){
      var slug = $('#add_library').attr("value");
      $.ajax({
        url: '/toonkor_collector2/add_library/',
        type: 'GET',
        data: {
            'slug': slug,
        },

        success: function(response) {
            console.log("success")
        },
      })
    });  
  });
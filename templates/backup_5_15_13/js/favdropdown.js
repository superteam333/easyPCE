$(document).ready(function() {
    $(".favButton").show();
    $('.getFavorites').bind('click', function(){
        $.get("../getfavorites", function(data) {
            $('.favDropdown').html("");
            for (var i in data) {
                if (i == 0) {
                    $('.favDropdown').append("<div style='margin: 5px 0px -15px 0px'> <a href= \'/courses/" + data[i][2] + "\'>"+ data[i][0] +  "</a></div><hr  /> ");

                }
				else if (i == data.length - 1) {
                    $('.favDropdown').append("<div style='margin: -15px 0px 0px 0px'> <a href= \'/courses/" + data[i][2] + "\'>"+ data[i][0] +  "</a></div>");
				
				}
                else {
                        $('.favDropdown').append("<div style='margin: -15px 0px -15px 0px'> <a href= \'/courses/" + data[i][2] + "\'>"+ data[i][0] +  "</a></div><hr  /> ");
                }
            }
            if (data.length == 0) {
                $('.favDropdown').html("No favorites yet.");
            }
        })
        ;
    });
});

$(".favorites").click(function(event_ref){
   event_ref.preventDefault();
});



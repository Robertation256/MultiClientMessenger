

$(window).load(function(){

    $("#login-btn").click(function(e){
        e.preventDefault();
        $.ajax({
            url:"/login",
            type:"POST",
            data:{
                username:$("#username").val(),
                avatar_id:"avatar"+$(".carousel-item.active").attr("id")
            },
            success: function(data){
                if (!data.status){
                    alert(data.msg);
                }
                else{
                    window.location.href="/chatroom";
                }
            }
        });
    })


    $(document).on("keypress", function(event) {
        // Number 13 is the "Enter" key on the keyboard
        if (event.which === 13) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        $("#login-btn").click();
        }
        });

});



$(window).ready(function(){
    $('.carousel').carousel({
        interval: false,
    });

});


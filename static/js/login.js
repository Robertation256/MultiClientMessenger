

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

});



$(window).ready(function(){
    $('.carousel').carousel({
        interval: false,
    });

});


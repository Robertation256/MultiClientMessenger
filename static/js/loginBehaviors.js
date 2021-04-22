avatar_id = 1;

$(window).load(function(){

    $("#next-btn").click(function(){
        if (avatar_id==15){
            avatar_id = 1;
        }
        else{
            avatar_id += 1;
        }
    })
    
    
    $("#prev-btn").click(function(){
        if (avatar_id==0){
            avatar_id = 15;
        }
        else{
            avatar_id -= 1;
        }
    })
    
    $("#login-btn").click(function(e){
        console.log("herere");
        if (avatar_id<10){
            avatar_id = "0"+avatar_id;
        }
        avatar_id = "avatar"+avatar_id;
        e.preventDefault();
        $.ajax({
            url:"/login",
            type:"POST",
            data:{
                username:$("#username").val(),
                avatar_id:avatar_id
            },
            success: function(data){
                window.location.href="/chatroom";
            }
        });
        
    })

});



$(window).ready(function(){
    $('.carousel').carousel({
        interval: false,
    });

});


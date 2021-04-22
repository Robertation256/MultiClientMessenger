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
        if (avatar_id==1){
            avatar_id = 15;
        }
        else{
            avatar_id -= 1;
        }
    })
    
    $("#login-btn").click(function(e){
        if (avatar_id<10){
            var result = "0"+avatar_id;
        }
        result = "avatar"+avatar_id;
        e.preventDefault();
        $.ajax({
            url:"/login",
            type:"POST",
            data:{
                username:$("#username").val(),
                avatar_id:result
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


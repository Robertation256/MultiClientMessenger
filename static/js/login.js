

$(window).load(function(){
    var avatar_id = 1;

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
        var result = "";
        if (avatar_id<10){
            result = "0"+avatar_id.toString();
        }
        result = "avatar"+result;
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


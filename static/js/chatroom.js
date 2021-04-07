$(window).load(function(){
    $("#connect-btn").click(function(){
        $.ajax({
            type:"get",
            url:"/connect",
            success:function(data){
                console.log("connect feedback");
                console.log(data);
            }

        });

     $("#refresh-btn").click(function(){
        $.ajax({
            type:"get",
            url:"/refresh",
            success:function(data){
                console.log("refresh feedback");
                console.log(data);
            }

            });


        });
    });

});
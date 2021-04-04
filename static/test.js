$(window).load(function(){
    $("#test-btn").click(function(){
        $.ajax({
                type:'post',
                url:'http://localhost:80/test?id=6666',
                data:{"token":"Some data here"},
                success:function(data){
                        console.log(data.msg);
                    }
                })



    });






});
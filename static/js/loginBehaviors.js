$("#divLogin").hide();
$(function() {
	$("#divLogin").show(500);
	console.log("start of js");

	// $("input[name='username']").on("click", function(){
	// 	var toAlert = "dalf";
	// 	alert(toAlert);
	// });

	$("label").on("click", function(){
		if ($(this).attr("for").indexOf("avatar") == 0){
			$(this).children().children().css("border-style", "solid");
			$(this).siblings().children().children().css("border-style", "none");
		};
	});

	var sth = false
	if (sth) {
		$("#divError").text("Error Message here");
		$("#divError").show(500);
	};
});
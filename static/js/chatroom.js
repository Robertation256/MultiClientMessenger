$(function() {
setTimeout(function(){  // wait a while after page is loaded
  autoRefresh = false;

  var secret = "zxcvbnm,./;lkjhg";
  var publicKey = $("#pubkey").val();
  var RSAcrypto = new JSEncrypt();
  RSAcrypto.setPublicKey(publicKey);
  var REFRESH_INTERVAL = 1000;  // time between two AutoRefreshes
  var refresh_id = null;
  var refresh_failure_count = 0;  // stop AutoRefresh when this large

  var my_username = "";
  var my_status = "OFFLINE";
  var curr_group = 0;
  var out_users = {};
  var in_users = {};
  var latest_timestamp = "00-00 00:00:00";
  var BASE_TIMESTAMP = "00-00 00:00:00";

  var max_message_bubble_letter_length = 25;


  function showAlert(str) {
    document.getElementById("divAlert").innerHTML = str;
    $("#divAlert").show(200).delay(3000).hide(200);
  }

  function encryptByDES(message, key) {
    var keyHex = CryptoJS.enc.Utf8.parse(key);
    var encrypted = CryptoJS.TripleDES.encrypt(message, keyHex, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7,
    });
    return encrypted.toString();
  }

  function decryptByDES(message, key) {
    var keyHex = CryptoJS.enc.Utf8.parse(key);

    var decrypted = CryptoJS.TripleDES.decrypt(message, keyHex, {
      mode: CryptoJS.mode.ECB,
      padding: CryptoJS.pad.Pkcs7,
    });
    return decrypted.toString(CryptoJS.enc.Utf8);
  }

  function connectOnLoad() {
    var secret_enc = RSAcrypto.encrypt(secret).toString();
    var test_msg_enc = encryptByDES("Hello World", secret);
    $.ajax({
      url: "/connect",
      type: "post",
      data: {
        "secret": secret_enc,
        "test_msg": test_msg_enc,
      },
      success: function(data_returned) {
        console.log("connectOnLoad status:", data_returned["status"]);
        if (data_returned["status"] == 1) {
          my_status = "ONLINE";
          showAlert("Encrypted channel established");
          console.log("connectOnLoad data:", data_returned);
          startAutoRefresh();
        }
        else {
          my_status = "OFFLINE";
          showAlert("Connection failed");
        }
        return data_returned["status"];
      },
      error: function() {
        return 0;
      },
    });
  }
  
  function refreshPage() {
    $.ajax({
      url: "/refresh",
      timeout: 1000,
      type: "get",
      success: function(data_refreshed) {
        my_status = "ONLINE";
        data = JSON.parse(decryptByDES(data_refreshed, secret));
        my_username = data["username"];
        curr_group = data["my_chat_group_id"];
        refreshDivUsers(data["out_group_users"], data["in_group_users"]);
        refreshDivChat(data["chat_messages"]);
        // console.log("refreshed success");
        refresh_failure_count = 0;
      },
      error: function() {
        console.log("refresh failed");
        // showAlert("Page refresh failed!");
        refresh_failure_count += 1;
       if (refresh_failure_count > 5) {
         my_status = "OFFLINE";
         // alert("Page refresh failed " +
         //   refresh_failure_count.toString() +
         //   " times in a row. AutoRefresh disabled.");
         stopAutoRefresh();
       }
      }
    });
    if (autoRefresh) {
      setTimeout(refreshPage, REFRESH_INTERVAL);
    }
  }

  function refreshDivUsers(refreshed_out_users, refreshed_in_users) {
    var i;
    var temp_user;
    var refreshed_out_usernames = [];
    var refreshed_in_usernames = [];
    var temp_id;
    var temp_html;
    
    $("#listOfPeople").children().remove();
    for (i=0; i<refreshed_in_users.length; i++) {
      temp_user = refreshed_in_users[i];
      out_users[temp_user["username"]] = {
        "username": temp_user["username"],
        "chat_group_id": temp_user["chat_group_id"],
        "avatar_id": temp_user["avatar_id"]
      };
      temp_html = '<div class="chat_list active_chat" id="user'+temp_user["username"]+'">'+
                  '<div class="chat_people">'+
                  '<div class="chat_img"> '+
                  '<img src="/static?file_name='+ temp_user["avatar_id"] + 
                  '.jpg" alt="sunil"> '+
                  '</div>' +
                  '<div class="chat_ib">' +
                  '<h5>'+ temp_user["username"] +'<span class="chat_date"></span></h5>' +
                  '<p></p>' +
                  '</div></div></div>';
      $("#listOfPeople").append(temp_html);
    }
    for (i=0; i<refreshed_out_users.length; i++) {
      temp_user = refreshed_out_users[i];
      out_users[temp_user["username"]] = {
        "username": temp_user["username"],
        "chat_group_id": temp_user["chat_group_id"],
        "avatar_id": temp_user["avatar_id"]
      };
      temp_html = '<div class="chat_list" id="user'+temp_user["username"]+'">'+
                  '<div class="chat_people">' + 
                  '<div class="chat_img"> '+
                  '<img src="/static?file_name='+ temp_user["avatar_id"] + 
                  '.jpg" alt="sunil"> '+
                  '</div>' +
                  '<div class="chat_ib">' +
                  '<h5>'+ temp_user["username"] +'<span class="chat_date"></span></h5>' +
                  '<p></p>' +
                  '</div></div></div>';
      $("#listOfPeople").append(temp_html);
    }
  }

  function refreshDivChat(chat_messages) {
    var i = 0;
    var temp_html;
    for (i=0; i<chat_messages.length; i++) {
      curr_msg = chat_messages[i];
      // new message

      var p_maxwidth = curr_msg["message"].length;
      if (p_maxwidth < 10) {
        p_maxwidth = p_maxwidth.toString() + "em";
      }
      else {
        p_maxwidth = "25em";
      }
      if (curr_msg["timestamp"] > latest_timestamp) {
        latest_timestamp = curr_msg["timestamp"];
        if (curr_msg["username"] != my_username) {  // incoming msg
          temp_id = curr_msg["timestamp"] + curr_msg["username"];
          temp_html = '<div class="incoming_msg" style="min-height:35px;"id="'+ temp_id +'">' +
                      '<div class="incoming_msg_img"> '+
                      '<img src="/static?file_name='+ curr_msg["avatar_id"] +
                      '.jpg" alt="sunil">'+
                      '</div>'+
                      '<div style="display:inline-block;height:100%;">'+
                      '<div class="received_msg" >'+ // style="postion:absolute;left:5px;"
                      '<div class="received_withd_msg">'+
                      '<p style="word-wrap:break-word;max-width:'+ p_maxwidth +';">'+
                      curr_msg["message"]+
                      '</p></div></div>'+
                      '<span class="time_date" style="float:left;">'+curr_msg["timestamp"]+'</span>'+
                      '</div></div>';
          $("#allMessages").append(temp_html);
        }
        else {
          temp_id = curr_msg["timestamp"] + curr_msg["username"];
          temp_html = '<div class="outgoing_msg" id="'+ temp_id +'">'+
                      '<div class="sent_msg">'+
                      '<p style="float:right;word-wrap:break-word;max-width:'+p_maxwidth+';">'+
                      curr_msg["message"]+'</p><br/>'+
                      '<span class="time_date" style="float:right;">'+ curr_msg["timestamp"] +'</span>'+
                      '</div></div>';
          $("#allMessages").append(temp_html);
        }
        document.getElementById("allMessages").scrollTop = 
          document.getElementById("allMessages").scrollHeight;
      }
    }
  }

  function startAutoRefresh() {  // automatically refresh page
    autoRefresh = true;
    refreshPage();
  }

  function stopAutoRefresh() {
    autoRefresh = false;
  }

  $(document).on("click", ".chat_list", function(){
    $(this).fadeOut(100).fadeIn(100);
    var user_tojoin = $(this).attr("id").slice(4,);
    var groupid_tojoin = out_users[user_tojoin]["chat_group_id"];
    if (groupid_tojoin == curr_group) {  // already in this group, do nothing
      return;
    }
    $("#allMessages").children().remove();  //Remove messages in previous group chat

    $.ajax({
      url: "/join?group_id="+groupid_tojoin,
      type: "get",
      success: function(join_result) {
        if (join_result["status"] == 1) {
          my_status = "INGROUP";
          curr_group = groupid_tojoin;
          latest_msg_timestamp = BASE_TIMESTAMP;
        }
        else {
          showAlert("Failed to join " + user_tojoin + "!");
          console.log("server joining", user_tojoin, "failed");
        }
      },
      error: function() {
        showAlert("Failed to join " + user_tojoin + "!");
        console.log("ajax joining", user_tojoin, "failed");
      }
    });
  });

  $(document).on("keypress", function(event) {
  // Number 13 is the "Enter" key on the keyboard
  if (event.which === 13) {
    // Cancel the default action, if needed
    event.preventDefault();
    // Trigger the button element with a click
    $(".msg_send_btn").click();
    }
  });

  $(".msg_send_btn").on("click", function() {
    var msg = $("#inputMessageBlah").val();
    $("#inputMessageBlah").attr("disabled","disabled");
    console.log("sendingmessage:", msg);
    $("#inputMessageBlah").val("");
    if (msg == "") {  // nothing to send
      $("#inputMessageBlah").removeAttr("disabled");
      return;
    }
    msg = encryptByDES(msg, secret);
    $.ajax({
      url: "/send_message",
      type: "post",
      data: {
        "message": msg
      },
      success: function(send_result) {
        if (send_result["status"] == 1) {
          // refreshPage();
        }
        else {
          console.log("send message failed");
          showAlert("Sending message failed!");
        }
        $("#inputMessageBlah").removeAttr("disabled");

      },
      error: function(){
        $("#inputMessageBlah").removeAttr("disabled");
      }
    });

  });

  $(window).on("beforeunload", function() {
    $("#logout-btn").click();
});

  $("#logout-btn").on("click", function() {
    $.ajax({
      url: "/log_out",
      type: "post",
      success: function(logout_result) {
        if (logout_result["status"] == 1) {
          console.log("logout success");
          window.location.href = "/login";
        }
        else {
          console.log("logout denied");
          showAlert("Logout failed");
        }
      },
      error: function() {
        console.log("logout denied");
        showAlert("Logout request denied!");
      }
    });
  });

  connectOnLoad();  // the start of everything

}, 500);  // wait after page is loaded
});







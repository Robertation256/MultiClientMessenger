$(function() {
setTimeout(function(){  // wait a while after page is loaded
  autoRefresh = false;

  var secret = "zxcvbnm,./;lkjhg";
  var publicKey = $("#pubkey").val();
  var RSAcrypto = new JSEncrypt();
  RSAcrypto.setPublicKey(publicKey);
  var REFRESH_INTERVAL = 5000;  // time between two AutoRefreshes
  var refresh_id = null;
  var refresh_failure_count = 0;  // stop AutoRefresh when this large

  var my_username = "";
  var my_status = "OFFLINE";
  var curr_group = 0;
  var out_users = {};
  var in_users = {};
  var latest_timestamp = "00-00 00:00:00";
  var BASE_TIMESTAMP = "00-00 00:00:00";

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
          showAlert("Auto connect success!");
          console.log("connectOnLoad data:", data_returned);
          $("#connect-btn").hide(500);
          $("#refresh-btn").show(500);
          startAutoRefresh();
        }
        else {
          my_status = "OFFLINE";
          showAlert("Auto connect failed! Please manually connect.");
          $("#connect-btn").show(500);
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
      timeout: REFRESH_INTERVAL,
      type: "get",
      success: function(data_refreshed) {
        my_status = "ONLINE";
        data = JSON.parse(decryptByDES(data_refreshed, secret));
        my_username = data["username"];
        curr_group = data["my_chat_group_id"];
        refreshDivUsers(data["out_group_users"], data["in_group_users"]);
        refreshDivChat(data["chat_messages"]);
        console.log("refreshed success");
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
    // to add into html, for out_group_users
    for (i=0; i<refreshed_out_users.length; i++) {
      refreshed_out_usernames.push(refreshed_out_users[i]["username"]);
    }
    for (i=0; i<refreshed_in_users.length; i++) {
      refreshed_in_usernames.push(refreshed_in_users[i]["username"]);
    }
    // first, clear current html page
    for (u in out_users) {
      temp_user = out_users[u];
      if (!refreshed_out_usernames.includes(temp_user["username"]) && 
          temp_user["ingroup"] == "FALSE") {
        out_users[u]["status"] = "OFFLINE";
        temp_id = "divUser" + temp_user["username"];
        if ($("#"+temp_id)) {
          $("#"+temp_id).hide(500);
          $("#"+temp_id).remove();
        }
      }
      if (!refreshed_in_usernames.includes(temp_user["username"]) && 
          temp_user["ingroup"] == "TRUE") {
        out_users[u]["status"] = "OFFLINE";
        temp_id = "divUser" + temp_user["username"];
        if ($("#"+temp_id)) {
          $("#"+temp_id).hide(500);
          $("#"+temp_id).remove();
        }
      }
    }
    // then, add into html page
    for (i=0; i<refreshed_out_users.length; i++) {
      temp_user = refreshed_out_users[i];
      if (out_users[temp_user["username"]]) {
        out_users[temp_user["username"]]["chat_group_id"] = temp_user["chat_group_id"];
        // already "ONLINE" means already in html
        if (out_users[temp_user["username"]]["status"] != "ONLINE") {
          out_users[temp_user["username"]]["status"] = "ONLINE";
          out_users[temp_user["username"]]["ingroup"] = "FALSE";
          temp_id = 'divUser' + temp_user["username"];
          temp_html = '<div class="DivUserEntry" id="' + temp_id + '">' + 
                      '<img src="/static?file_name=' + temp_user["avatar_id"] + 
                      '.jpg" class="AvatarImg">' + 
                      '<text class="UserEntryName>' + temp_user["username"] + '</text>' + 
                      '</div>';
          $("#divUsers").prepend(temp_html);
          $("#"+temp_id).show(500).fadeOut(100).fadeIn(100);
        }
      }
      else {
        out_users[temp_user["username"]] = {
          "username": temp_user["username"], 
          "avatar_id": temp_user["avatar_id"], 
          "chat_group_id": temp_user["chat_group_id"], 
          "status": "ONLINE",
          "ingroup": "FALSE"
        };
        temp_id = 'divUser' + temp_user["username"];
        temp_html = '<div class="DivUserEntry" id="' + temp_id + '">' + 
                    '<img src="/static?file_name=' + temp_user["avatar_id"] + 
                    '.jpg" class="AvatarImg">' + 
                    '<text class="UserEntryName">' + temp_user["username"] + '</text>' + 
                    '</div>';
        $("#divUsers").prepend(temp_html);
        $("#"+temp_id).show(500).fadeOut(100).fadeIn(100);
      }
    }
    for (i=0; i<refreshed_in_users.length; i++) {
      temp_user = refreshed_in_users[i];
      if (out_users[temp_user["username"]]) {
        out_users[temp_user["username"]]["chat_group_id"] = temp_user["chat_group_id"];
        // already "ONLINE" means already in html
        if (out_users[temp_user["username"]]["status"] != "ONLINE") {
          out_users[temp_user["username"]]["status"] = "ONLINE";
          out_users[temp_user["username"]]["ingroup"] = "TRUE";
          temp_id = 'divUser' + temp_user["username"];
          temp_html = '<div class="DivUserEntry" id="' + temp_id + '">' + 
                      '<img src="/static?file_name=' + temp_user["avatar_id"] + 
                      '.jpg" class="AvatarImg">' + 
                      '<text class="UserEntryName>' + temp_user["username"] + '</text>' + 
                      '</div>';
          $("#divUsers").prepend(temp_html);
          $("#"+temp_id).css("border-style", "inset").css("background-color", "lightgrey");
          $("#"+temp_id).show(500).fadeOut(100).fadeIn(100);
        }
      }
      else {
        out_users[temp_user["username"]] = {
          "username": temp_user["username"], 
          "avatar_id": temp_user["avatar_id"], 
          "chat_group_id": temp_user["chat_group_id"], 
          "status": "ONLINE",
          "ingroup": "TRUE"
        };
        temp_id = 'divUser' + temp_user["username"];
        temp_html = '<div class="DivUserEntry" id="' + temp_id + '">' + 
                    '<img src="/static?file_name=' + temp_user["avatar_id"] + 
                    '.jpg" class="AvatarImg">' + 
                    '<text class="UserEntryName>' + temp_user["username"] + '</text>' + 
                    '</div>';
        $("#divUsers").prepend(temp_html);
        $("#"+temp_id).css("border-style", "inset").css("background-color", "lightgrey");
        $("#"+temp_id).show(500).fadeOut(100).fadeIn(100);
      }
    }
  }

  function refreshDivChat(chat_messages) {
    console.log("chat_messages:", chat_messages);
    var i = 0;
    var temp_html;
    for (i=0; i<chat_messages.length; i++) {
      curr_msg = chat_messages[i];
      // new message
      if (curr_msg["timestamp"] > latest_timestamp) {
        latest_timestamp = curr_msg["timestamp"];
        if (curr_msg["username"] != my_username) {  // incoming msg
          temp_id = curr_msg["timestamp"] + curr_msg["username"];
          temp_html = '<div class="DivChatInMsg" id="' + temp_id + '">' + 
                      curr_msg["message"] + 
                      '</div>';
          $("#divChat").append(temp_html);
          $("#"+temp_id).show(500);
        }
        else {
          temp_id = curr_msg["timestamp"] + curr_msg["username"];
          temp_html = '<div class="DivChatOutMsg" id="' + temp_id + '">' + 
                      curr_msg["message"] + 
                      '</div>';
          $("#divChat").append(temp_html);
          $("#"+temp_id).show(500);
        }
      }
    }
  }

  function startAutoRefresh() {  // automatically refresh page
    autoRefresh = true;
    refreshPage();
//    if (!refresh_id) {  // AutoRefresh off
//      refresh_id = setInterval(function() {
//        refreshPage();
//      }, REFRESH_INTERVAL);
//    }
//    else {  // AutoRefresh already on
//      stopAutoRefresh();
//      refresh_id = setInterval(function() {
//        refreshPage();
//      }, REFRESH_INTERVAL);
//    }
  }

  function stopAutoRefresh() {
    autoRefresh = false;
//    if (refresh_id) {
//      clearInterval(refresh_id);
//      refresh_id = null;
//    }
  }

  $(document).on("click", ".DivUserEntry", function(){
    $(this).fadeOut(100).fadeIn(100);
    var user_tojoin = $(this).children().filter($("text")).html();
    var groupid_tojoin = out_users[user_tojoin]["chat_group_id"];
    if (groupid_tojoin == curr_group) {  // already in this group, do nothing
      return;
    }
    $.ajax({
      url: "/join?group_id="+groupid_tojoin,
      type: "get",
      success: function(join_result) {
        if (join_result["status"] == 1) {
          console.log("server joining", user_tojoin, "success");
          my_status = "INGROUP";
          curr_group = groupid_tojoin;
          latest_msg_timestamp = BASE_TIMESTAMP;
          refreshPage();
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

  $("#connect-btn").on("click", function() {
    showAlert("Starting Connection!");
    connectOnLoad();
  });

  $("#refresh-btn").on("click", function() {
    showAlert("Starting AutoRefresh!");
    startAutoRefresh();
  });

  $("#send-btn").on("click", function() {
    var msg = $("#inputSendMsg").val();
    $("#inputSendMsg").val("");
    if (msg == "") {  // nothing to send
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
          console.log("send message success");
          refreshPage();
        }
        else {
          console.log("send message failed");
          showAlert("Sending message failed!");
        }
      },
    });
  });

  connectOnLoad();  // the start of everything

}, 500);  // wait after page is loaded
});



    // for (i=0; i<refreshed_out_users.length; i++) {
    //   temp_user = refreshed_out_users[i];
    //   refreshed_out_usernames.push(temp_user["username"]);
    //   if (out_users[temp_user["username"]]) {  // already in cache
    //     out_users[temp_user["username"]]["chat_group_id"] = temp_user["chat_group_id"];
    //     if (out_users[temp_user["username"]]["status"] != "ONLINE") {
    //       out_users[temp_user["username"]]["status"] = "ONLINE";
    //       temp_id = 'divUser' + temp_user["username"];
    //       temp_html = '<div class="DivUserEntry" id="' + temp_id + 
    //                   '">' + 
    //                   '<text>' + temp_user["username"] + '</text>' + 
    //                   '</div>';
    //       $("#divUsers").prepend(temp_html);
    //       $("#"+temp_id).show(500).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100);
    //     }
    //   }
    //   else {  // new to cache
    //     out_users[temp_user["username"]] = {
    //       "username": temp_user["username"],
    //       "avatar_id": temp_user["avatar_id"],
    //       "chat_group_id": temp_user["chat_group_id"],
    //       "status": "ONLINE",
    //     };
    //     temp_id = 'divUser' + temp_user["username"];
    //     temp_html = '<div class="DivUserEntry" id="' + temp_id + 
    //                 '">' + 
    //                 '<text>' + temp_user["username"] + '</text>' + 
    //                 '</div>';
    //     $("#divUsers").prepend(temp_html);
    //     $("#"+temp_id).show(500).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100);
    //   }
    // }
    // // to remove from html
    // for (i in out_users) {
    //   temp_user = out_users[i];
    //   if (!refreshed_out_usernames.includes(temp_user["username"])) {  // not curr online
    //     out_users[i]["status"] = "OFFLINE";
    //     temp_id = 'divUser' + temp_user["username"];
    //     if ($("#"+temp_id)) {  // if html on page
    //       $("#"+temp_id).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100).hide(500);
    //       $("#"+temp_id).remove();
    //     }
    //   }
    // }







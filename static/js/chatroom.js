$(function() {
setTimeout(function(){  // wait a while after page is loaded
  autoRefresh = false;

  var secret = "zxcvbnm,./;lkjhg";
  var publicKey = $("#pubkey").val();
  var RSAcrypto = new JSEncrypt();
  RSAcrypto.setPublicKey(publicKey);
  var REFRESH_INTERVAL = 2000;  // time between two AutoRefreshes
  var refresh_id = null;
  var refresh_failure_count = 0;  // stop AutoRefresh when this large

  var my_status = "OFFLINE";
  var curr_group = 0;
  var out_users = {};
  var in_users = {};

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
    var test_msg_enc = encryptByDES("Hello World", secret).toString();
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
        refreshDivUsers(data["out_group_users"], data["in_group_users"]);
        refreshDivChat(data);
        console.log("refreshed success");
        refresh_failure_count = 0;
      },
      error: function() {
        console.log("refresh failed");
        showAlert("Page refresh failed!");
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
    if (autoRefresh){
        setTimeout(refreshPage, REFRESH_INTERVAL);
        }
  }

  function refreshDivUsers(refreshed_out_users, refershed_in_users) {
    var i;
    var temp_user;
    var refreshed_out_usernames = [];
    var refreshed_in_usernames = [];
    var temp_id;
    var temp_html;
    // to add into html
    for (i=0; i<refreshed_out_users.length; i++) {
      temp_user = refreshed_out_users[i];
      refreshed_out_usernames.push(temp_user["username"]);
      if (out_users[temp_user["username"]]) {  // already in cache
        if (out_users[temp_user["username"]]["status"] != "ONLINE") {
          out_users[temp_user["username"]]["status"] = "ONLINE";
          temp_id = 'divUser' + temp_user["username"];
          temp_html = '<div class="DivUserEntry" id="' + temp_id + 
                      '">' + 
                      '<text>' + temp_user["username"] + '</text>' + 
                      '</div>';
          $("#divUsers").prepend(temp_html);
          $("#"+temp_id).show(500).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100);
        }
      }
      else {  // new to cache
        out_users[temp_user["username"]] = {
          "username": temp_user["username"],
          "avatar_id": temp_user["avatar_id"],
          "chat_group_id": temp_user["chat_group_id"],
          "status": "ONLINE",
        };
        temp_id = 'divUser' + temp_user["username"];
        temp_html = '<div class="DivUserEntry" id="' + temp_id + 
                    '">' + 
                    '<text>' + temp_user["username"] + '</text>' + 
                    '</div>';
        $("#divUsers").prepend(temp_html);
        $("#"+temp_id).show(500).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100);
      }
    }
    // to remove from html
    for (i in out_users) {
      temp_user = out_users[i];
      if (!refreshed_out_usernames.includes(temp_user["username"])) {  // not curr online
        out_users[i]["status"] = "OFFLINE";
        temp_id = 'divUser' + temp_user["username"];
        if ($("#"+temp_id)) {  // if html on page
          $("#"+temp_id).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100).hide(500);
          $("#"+temp_id).remove();
        }
      }
    }
  }

  function refreshDivChat(data_refreshed) {
    console.log("refreshed data:", data_refreshed);
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
          console.log(join_result);
          console.log("server joining", user_tojoin, "success");
          my_status = "INGROUP";
          curr_group = groupid_tojoin;
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

  connectOnLoad();  // the start of everything



}, 500);  // wait after page is loaded
});








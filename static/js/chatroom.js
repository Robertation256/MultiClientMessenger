$(function() {
setTimeout(function(){  // wait a while after page is loaded
  var secret = "zxcvbnm,./;lkjhg";
  var publicKey = $("#pubkey").val();
  var RSAcrypto = new JSEncrypt();
  RSAcrypto.setPublicKey(publicKey);
  var REFRESH_INTERVAL = 5000;  // time between two AutoRefreshes
  var refresh_id = null;
  var refresh_failure_count = 0;  // stop AutoRefresh when this large

  var user_status = "OFFLINE";
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
          user_status = "ONLINE";
          showAlert("Auto connect success!");
          $("#connect-btn").hide(500);
          $("#refresh-btn").show(500);
          startAutoRefresh();
        }
        else {
          user_status = "OFFLINE";
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
      type: "get",
      success: function(data_refreshed) {
        user_status = "ONLINE";
        data_refreshed = JSON.parse(decryptByDES(data_refreshed, secret));
        refreshDivUsers(data_refreshed["out_group_users"]);
        refreshDivChat(data_refreshed);
        console.log("refreshed success, data:", data_refreshed);
        refresh_failure_count = 0;
      },
      error: function() {
        console.log("refresh failed");
        showAlert("Page refresh failed!");
        refresh_failure_count += 1;
        if (refresh_failure_count > 2) {
          user_status = "OFFLINE";
          // alert("Page refresh failed " + 
          //   refresh_failure_count.toString() + 
          //   " times in a row. AutoRefresh disabled.");
          stopAutoRefresh();
        }
      }
    });
  }

  function refreshDivUsers(refreshed_users) {
    var i;
    var temp_user;
    var temp_id;
    var temp_html;
    // to add into html
    for (i=0; i<refreshed_users.length; i++) {
      temp_user = refreshed_users[i];
      if (out_users[temp_user["username"]]) {  // already in cache
        if (out_users[temp_user["username"]]["status"] != "ONLINE") {
          out_users[temp_user["username"]]["status"] = "ONLINE";
          temp_id = 'divUser' + temp_user["username"];
          temp_html = '<div class="DivUserEntry" id="' + temp_id + 
                      '">' + temp_user["username"] + '</div>';
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
                    '">' + temp_user["username"] + '</div>';
        $("#divUsers").prepend(temp_html);
        $("#"+temp_id).show(500).fadeOut(100).fadeIn(100).fadeOut(100).fadeIn(100);
      }
    }
    // to remove from html
    for (i=0; i<out_users.length; i++) {
      temp_user = out_users[i];
      console.log(temp_user);
    }
  }

  function refreshDivChat(data_refreshed) {
    console.log("refreshed in group users:", data_refreshed["in_group_users"]);
  }

  function startAutoRefresh() {  // automatically refresh page
    if (!refresh_id) {  // AutoRefresh off
      refresh_id = setInterval(function() {
        refreshPage();
      }, REFRESH_INTERVAL);
    }
    else {  // AutoRefresh already on
      stopAutoRefresh();
      refresh_id = setInterval(function() {
        refreshPage();
      }, REFRESH_INTERVAL);
    }
  }

  function stopAutoRefresh() {
    if (refresh_id) {
      clearInterval(refresh_id);
      refresh_id = null;
    }
  }

  $("#connect-btn").on("click", function(){
    connectOnLoad();
  });

  $("#refresh-btn").on("click", function(){
    showAlert("Starting AutoRefresh!");
    startAutoRefresh();
  });

  connectOnLoad();  // the start of everything



}, 500);  // wait after page is loaded
});








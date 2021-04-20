
$(function() {
setTimeout(function(){  // wait a while after page is loaded
  var secret = "zxcvbnm,./;lkjhg";
  var publicKey = $("#pubkey").val();
  var RSAcrypto = new JSEncrypt();
  RSAcrypto.setPublicKey(publicKey);
  var user_status = "OFFLINE";
  var curr_group = 0;
  var refresh_id = null;
  var refresh_failure_count = 0;

  function showAlert(str) {
    document.getElementById("divAlert").innerHTML = str;
    $("#divAlert").show(100).delay(2000).hide(100);
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
    var decrypted = CryptoJS.TripleDES.decrypt(message, keyHex);
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
          $("#connect-btn").hide(100);
          $("#refresh-btn").show(100);
          startAutoRefresh();
        }
        else {
          user_status = "OFFLINE";
          showAlert("Auto connect failed! Please manually connect.");
          $("#connect-btn").show(100);
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
        console.log("refreshed success, data:", data_refreshed);
        refresh_failure_count = 0;
      },
      error: function() {
        console.log("refresh failed");
        refresh_failure_count += 1;
        showAlert("Page refresh failed!");
        if (refresh_failure_count > 2) {
          showAlert("Page refresh failed " + 
            refresh_failure_count.toString() + 
            " times in a row. AutoRefresh disabled.");
          stopAutoRefresh();
        }
      }
    });
  }

  function startAutoRefresh() {  // automatically refresh page
    if (!refresh_id) {
      refresh_id = setInterval(function() {
        refreshPage();
      }, 3000);
    }
    else {
      stopAutoRefresh();
      refresh_id = setInterval(function() {
        refreshPage();
      }, 3000);
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
    stopAutoRefresh();
    refreshPage();
    startAutoRefresh();
  });

  connectOnLoad();



}, 1000);  // wait for 1000ms after page is loaded
});








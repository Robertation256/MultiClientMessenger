$("#connect-btn").hide();

$(function() {setTimeout(function(){
  var secret = "zxcvbnm,./;lkjhg";
  var publicKey = $("#pubkey").val();
  var RSAcrypto = new JSEncrypt();
  RSAcrypto.setPublicKey(publicKey);

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
          $("#connect-btn").hide(100);
        }
        return data_returned["status"];
      },
      error: function() {
        return 0;
      },
    });
  }

  $("#connect-btn").on("click", connectOnLoad);
  if (connectOnLoad() != 1) {
    showAlert("Auto connect failed, please manually connect...");
    $("#connect-btn").show(100);
  }


}, 1000);  // wait for 1000ms after page is loaded
});








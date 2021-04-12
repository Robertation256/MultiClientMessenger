$(window).load(function(){

    // This the secret for symmetric encryption. Should be 16 or 24 bytes long and randomized.
    var secret = "zxcvbnm,./;lkjhg";

    var publicKey = $("#pubkey").val();
    var RSAcrypto = new JSEncrypt();
    RSAcrypto.setPublicKey(publicKey);


    $('#connect-btn').click(function(event) {


      // Encrypt with the public key...
      var encrypted_secret = RSAcrypto.encrypt(secret);
      encrypted_secret = encrypted_secret.toString();

      var test_msg = "Hello World"; //This part should also be randomized.
      var symmetrically_encrypted_test_msg = encryptByDES(test_msg,secret).toString();

      console.log("symmetric encryption:"+symmetrically_encrypted_test_msg)
      $.ajax({
        url:"/connect",
        type:"post",
        data:{
            "secret":encrypted_secret,
            "test_msg":symmetrically_encrypted_test_msg
        },
        success:function(data){
            console.log(data);
        }
      });


      // Decrypt with the private key...
//      var decrypt = new JSEncrypt();
//      decrypt.setPrivateKey($('#privkey').val());
//      var uncrypted = decrypt.decrypt(encrypted);
//
//      // Now a simple check to see if the round-trip worked.
//      if (uncrypted == $('#input').val()) {
//        alert('It works!!!');
//      }
//      else {
//        alert('Something went wrong....');
//      }


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



    function encryptByDES(message, key) {
    var keyHex = CryptoJS.enc.Utf8.parse(key);
    var encrypted = CryptoJS.TripleDES.encrypt(message, keyHex, {
        mode: CryptoJS.mode.ECB,
        padding: CryptoJS.pad.Pkcs7
    });
    return encrypted.toString();
    }

});
});




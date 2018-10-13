function handleSignInClick(event) {
    // Ideally the button should only show up after gapi.client.init finishes, so that this
    // handler won't be called before OAuth is initialized.
    gapi.auth2.getAuthInstance().signIn();
}

function initBrowserWithOAuth() {

  var scope = "https://www.googleapis.com/auth/userinfo.profile";
  // Note:  to use Google platforms (GCS and Genomics) add the following scopes
  //      "https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/genomics https://www.googleapis.com/auth/devstorage.read_only",
  var client_id = "YOUR CLIENT ID HERE";

  gapi.load('client:auth2', initClient);


  function updateSigninStatus(isSignedIn) {

      var user = gapi.auth2.getAuthInstance().currentUser.get();
      igv.oauth.google.access_token = user.getAuthResponse().access_token;
  }

  function initClient() {

      gapi.client.init({
          'clientId': client_id,
          'scope': scope

      }).then(function () {

          var user = gapi.auth2.getAuthInstance().currentUser.get();
          if(user) {
              igv.oauth.google.access_token = user.getAuthResponse().access_token;
          }

          var $b = $("#signinbutton");
          $b.removeAttr('disabled');

          initBrowser();
      });

      gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);
      gapi.auth2.getAuthInstance().currentUser.listen(updateSigninStatus);

  };
}

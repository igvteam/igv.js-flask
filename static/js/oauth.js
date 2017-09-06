function handleSignInClick(event) {
    // Ideally the button should only show up after gapi.client.init finishes, so that this
    // handler won't be called before OAuth is initialized.
    gapi.auth2.getAuthInstance().signIn();
}

function initBrowserWithOAuth() {
  var scope = "https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/genomics https://www.googleapis.com/auth/devstorage.read_only https://www.googleapis.com/auth/userinfo.profile",
          client_id = "661332306814-8nt29308rppg325bkq372vli8nm3na14.apps.googleusercontent.com";

  gapi.load('client:auth2', initClient);


  function updateSigninStatus(isSignedIn) {

      var user = gapi.auth2.getAuthInstance().currentUser.get();
      oauth.google.access_token = user.getAuthResponse().access_token;
  }

  function initClient() {

      gapi.client.init({
          'clientId': client_id,
          'scope': scope

      }).then(function () {

          var user = gapi.auth2.getAuthInstance().currentUser.get();
          if(user) {
              oauth.google.access_token = user.getAuthResponse().access_token;
          }

          var $b = $("#signinbutton");
          $b.removeAttr('disabled');

          initBrowser();
      });

      gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);
      gapi.auth2.getAuthInstance().currentUser.listen(updateSigninStatus);

  };
}

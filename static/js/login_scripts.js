document.addEventListener("DOMContentLoaded", function() {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    if(window.innerWidth > 500){
      usernameInput.focus();
      usernameInput.click();
    }

    document.addEventListener("keydown", function(event) {
      if (event.key === "ArrowDown") {
        event.preventDefault();
        passwordInput.focus();
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        usernameInput.focus();
      }
    });
});

function showLoadIcon() {
    const loader = document.getElementById('loader')
    loader.style.display = "block";
}

function showPassword(){
    const password = document.getElementById("password");
    const eye = document.getElementById("eye");
    const eyeSlash = document.getElementById("eye-slash")

    if (eyeSlash.style.display == "block") {
        eyeSlash.style.display = "none";
        eye.style.display = "block";
        password.type = "text";
    }else{
        eyeSlash.style.display = "block";
        eye.style.display = "none";
        password.type = "password";
    }
}
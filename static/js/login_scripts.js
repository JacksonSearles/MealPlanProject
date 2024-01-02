function showDiv() {
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

const locked = document.querySelector("#lock");
const passowrd = document.querySelector("#password");
const icon = locked.querySelector("i");

locked.addEventListener("click", () => {
  if (passowrd.type == "password") {
    passowrd.type = "text";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  } else {
    passowrd.type = "password";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  }
});
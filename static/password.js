
const locked = document.querySelectorAll("#lock");
const passowrd = document.querySelectorAll("#password");


locked.forEach((btn,index)=>{
btn.addEventListener("click", () => {
    const icon = btn.querySelector("i");
  if (passowrd[index].type === "password") {
    passowrd[index].type = "text";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  } else {
    passowrd[index].type = "password";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  }
});
});


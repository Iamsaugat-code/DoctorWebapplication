const btn1 = document.querySelector("#menubtn")
const menu1 = document.querySelector("#menus")
const arrow = document.getElementById("arrow");

btn1.addEventListener("click",(e)=>{
    e.stopPropagation()
    menu1.classList.toggle("hidden")
    arrow.classList.toggle("fa-sort-down")
    arrow.classList.toggle("fa-sort-up")

})
menu1.addEventListener("click",(e)=>{
e.stopPropagation()
})

document.addEventListener("click",(e)=>{
        menu1.classList.add("show")
        label.forEach(el =>{
            el.classList.add("show")
        });
});

document.querySelectorAll('a[href="#"]').forEach(a=>{
a.addEventListener("click",(e)=>{
e.preventDefault()
})
});

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


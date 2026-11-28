

const month = document.querySelector("#month");
const month_day1 = document.querySelector("#month_day1");
const month_day2 = document.querySelector("#month_day2");
const month_day3 = document.querySelector("#month_day3");
const select_day1 = document.querySelector("#select_day1");
const select_day2 = document.querySelector("#select_day2");
const select_day3 = document.querySelector("#select_day3");


month.addEventListener("change",()=>{

  const [y, m] = month.value.split("-");
  const last_day = new Date(y, m, 0).getDate();

  month_day1.min = `${y}-${m}-01`;
  month_day1.max = `${y}-${m}-${String(last_day).padStart(2, "0")}`;
  month_day1.value = `${y}-${m}-01`;

  month_day2.min = `${y}-${m}-01`;
  month_day2.max = `${y}-${m}-${String(last_day).padStart(2,"0")}`
  month_day2.value = `${y}-${m}-01`;

  month_day3.min = `${y}-${m}-01`;
  month_day3.max = `${y}-${m}-${String(last_day).padStart(2,"0")}`
  month_day3.value = `${y}-${m}-01`;

  const date = new Date(month.value + "-01");
  const monthName = date.toLocaleDateString("en-US", {
        month: "short",
        year: "numeric"
    });

document.querySelector("#months_value").value = monthName

});


month_day1.addEventListener("click",()=>{
    month_day1.showPicker()
})
month_day2.addEventListener("click",()=>{
    month_day2.showPicker()
})
month_day3.addEventListener("click",()=>{
    month_day3.showPicker()
})



month_day1.addEventListener("change",()=>{
    if(month_day1.value){
        const d = new Date(month_day1.value + 'T00:00:00');
        const day = d.toLocaleDateString('en-US',{weekday:'short'});
        select_day1.textContent = `${day} (${d.getDate()})`
        document.querySelector("#day_one").value = `${day} (${d.getDate()})`

    }
    else{
        select_day1.textContent=" "
    }
})

month_day2.addEventListener("change",()=>{
    if(month_day2.value){
        const d = new Date(month_day2.value + 'T00:00:00');
        const day = d.toLocaleDateString('en-US',{weekday:'short'});
        select_day2.textContent = `${day} (${d.getDate()})`
        document.querySelector("#day_two").value = `${day} (${d.getDate()})`

    }
    else{
        select_day2.textContent=" "
    }
})

month_day3.addEventListener("change",()=>{
    if(month_day3.value){
        const d = new Date(month_day3.value + 'T00:00:00');
        const day = d.toLocaleDateString('en-US',{weekday:'short'});
        select_day3.textContent = `${day} (${d.getDate()})`
        document.querySelector("#day_three").value = `${day} (${d.getDate()})`

    }
    else{
        select_day3.textContent=" "
    }
})


const f_time = document.querySelector("#from_time")
const t_time = document.querySelector("#to_time")



function checkTime() {
  if (f_time.value && t_time.value && t_time.value <= f_time.value) {
    t_time.value = "";
    alert("To time must be later than From time");
  }
}

f_time.addEventListener("change", () => {
  t_time.min = f_time.value;
  checkTime();
});
t_time.addEventListener("change", checkTime);




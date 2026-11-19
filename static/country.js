

const dis = document.querySelector("#district")
const selected = dis.dataset.selected
console.log(selected)

fetch("https://raw.githubusercontent.com/abinrimal/nepal-administrative-divisions-json/main/districts.json").then(
  response => response.json()
).then(data =>{

  data.sort((a,b)=>a.name_en.localeCompare(b.name_en))
  data.forEach(items => {
    const option = document.createElement("option")
    option.value = items.name_en;
    option.textContent = items.name_en;
    dis.appendChild(option);
    
  });
     if (selected) {
            district.value = selected;
        }
  
}).catch(error => console.log(error));

const vdc = document.querySelector("#vdc")
const selectvdc = vdc.dataset.selected.trim()
fetch("https://raw.githubusercontent.com/abinrimal/nepal-administrative-divisions-json/main/local_levels.json").then(response => response.json()).then(data =>{
  data.sort((a,b)=> a.name_en.localeCompare(b.name_en))
  data.forEach(items =>{
    option = document.createElement("option");
    option.value = items.name_en;
    option.textContent = items.name_en;
    vdc.appendChild(option)
  });
  if (selectvdc){
    vdc.value = selectvdc
  }

});

  const input = document.getElementById('imageinput');
  const img = document.getElementById('preview');

  input.addEventListener('change', function () {
    const file = this.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (e) {
      img.src = e.target.result;
      img.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  });


fetch("https://raw.githubusercontent.com/abinrimal/nepal-administrative-divisions-json/main/districts.json").then(
  response => response.json()
).then(data =>{

  data.sort((a,b)=>a.name_en.localeCompare(b.name_en))
  let selectbtn = document.querySelector("#district")
  data.forEach(items => {
    const option = document.createElement("option")
    option.value = items.name_en;
    option.textContent = items.name_en;
    selectbtn.appendChild(option);
    
  });
  
}).catch(error => console.log(error));


fetch("https://raw.githubusercontent.com/abinrimal/nepal-administrative-divisions-json/main/local_levels.json").then(response => response.json()).then(data =>{

  const vdc = document.querySelector("#vdc")
  data.sort((a,b)=> a.name_en.localeCompare(b.name_en))
  data.forEach(items =>{
    option = document.createElement("option");
    option.value = items.name_en;
    option.textContent = items.name_en;
    vdc.appendChild(option)
  });
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

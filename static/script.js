let defaultLinks = [
{
name:"Otp Spammer",
url:"https://rifanctr.github.io/Otp-Spammer/"
},
{
name:"Phising Location",
url:"https://rifanctr.github.io/wtahsbdod/"
},

{
name:"Local House",
url:"https://rifanctr.github.io/upload-pc/"
},

{
name:"Termux App",
url:"https://github.com/termux/termux-app.git"
},

{
name:"Linux Software",
url:"https://github.com/luong-komorebi/Awesome-Linux-Software.git"
},

{
name:"News Website",
url:"https://rifanctr.github.io/berita-terbaru/"
}

];

let links=
JSON.parse(
localStorage.getItem("database")
);

if(!links){

links=defaultLinks;

localStorage.setItem(
"database",
JSON.stringify(links)
);

}

function save(){

localStorage.setItem(
"database",
JSON.stringify(links)
);

}

function addLink(){

let name=
document.getElementById("name").value;

let url=
document.getElementById("url").value;

if(!name||!url){

alert("Fill all fields");

return;

}

links.push({
name,
url
});

save();

renderLinks();

document.getElementById("name").value="";
document.getElementById("url").value="";

}

function removeLink(i){

links.splice(i,1);

save();

renderLinks();

}

function renderLinks(){

let search=
document
.getElementById("search")
.value
.toLowerCase();

let html="";

links
.filter(
x=>x.name
.toLowerCase()
.includes(search)
)

.forEach((x,i)=>{

html+=`

<div class="card">

<div class="linkInfo">

<h3>${x.name}</h3>

<p>${x.url}</p>

</div>

<div class="action">

<button
onclick="
window.open('${x.url}')
"
>

Open

</button>

<button
onclick="
removeLink(${i})
"
>

Delete

</button>

</div>

</div>

`;

});

document
.getElementById("database")
.innerHTML=html;

}

renderLinks();
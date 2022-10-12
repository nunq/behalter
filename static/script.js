function send() {
  l = document.getElementById("new-link");
  t = document.getElementById("new-title");
  d = document.getElementById("new-description").value;
  n = document.getElementById("new-note").value;
  ta = document.getElementById("new-tags").value;

  l.reportValidity();
  t.reportValidity();

  fetch("/api/add?link="+encodeURIComponent(l.value)+"&note="+encodeURIComponent(n)+"&tags="+encodeURIComponent(ta)+"&description="+encodeURIComponent(d)+"&title="+encodeURIComponent(t.value))
    .then((response) => response.json())
    .then((data) => console.log(data));
}

function getlinkinfo() {
  l = document.getElementById("new-link");
  t = document.getElementById("new-title");

  l.reportValidity();

  fetch("/api/linkinfo?link="+encodeURIComponent(l.value))
    .then((response) => response.json())
    .then((data) => t.value = data["title"]);
}

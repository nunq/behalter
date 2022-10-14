function send() {
  l = document.getElementById("new-link");
  t = document.getElementById("new-title");
  d = document.getElementById("new-detail").value;
  n = document.getElementById("new-note").value;
  ta = document.getElementById("new-tags").value;

  if(l.value == "" || t.value == "") {
    l.reportValidity();
    t.reportValidity();
    return
  }

  fetch("/api/add?link="+encodeURIComponent(l.value)+"&note="+encodeURIComponent(n)+"&tags="+encodeURIComponent(ta)+"&detail="+encodeURIComponent(d)+"&title="+encodeURIComponent(t.value))
    .then((response) => response.json())
    .then((data) => console.log(data));
}

function setlinkinfo(data) {
  document.getElementById("new-title").value = data["title"];
  document.getElementById("new-detail").value = data["detail"];
}

function getlinkinfo() {
  l = document.getElementById("new-link");

  if(l.value == "") {
    l.reportValidity();
    return
  }

  document.getElementById("new-title").placeholder = "fetching title...";
  document.getElementById("new-detail").placeholder = "fetching detail...";

  fetch("/api/linkinfo?link="+encodeURIComponent(l.value))
    .then((response) => response.json())
    .then((data) => setlinkinfo(data));
}

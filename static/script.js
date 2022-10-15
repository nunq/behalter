function checkerror(json) {
  if(json["result"] == "error") {
    alert(json["res-text"]);
  }
}

function add() {
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

  fetch("/api/bm/add?link="+encodeURIComponent(l.value)+"&note="+encodeURIComponent(n)+"&tags="+encodeURIComponent(ta)+"&detail="+encodeURIComponent(d)+"&title="+encodeURIComponent(t.value))
    .then((response) => response.json())
    .then((data) => checkerror(data));
}

function deletebm(bookmark) {
  if(confirm("really delete "+bookmark.dataset.title+" ?")) {
    fetch("/api/bm/delete?id="+bookmark.dataset.id)
      .then((response) => response.json())
      .then((data) => checkerror(data));
  }
}

function filterbytag(tag) {
  console.log(tag.innerHTML);
  // TODO send to /search?tag= ...
}

function resetfields() {
  document.getElementById("new-title").placeholder = "title";
  document.getElementById("new-detail").placeholder = "detail";
  document.getElementById("new-title").value = "";
  document.getElementById("new-detail").value = "";
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

  if(! /^http/.test(l.value)) {
    return
  }

  document.getElementById("new-title").placeholder = "fetching title...";
  document.getElementById("new-detail").placeholder = "fetching detail...";

  fetch("/api/bm/linkinfo?link="+encodeURIComponent(l.value))
    .then((response) => response.json())
    .then((data) => setlinkinfo(data));
}

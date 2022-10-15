"use strict";

const l = document.getElementById("new-link");
const t = document.getElementById("new-title");
const d = document.getElementById("new-detail");
const n = document.getElementById("new-note");
const ta = document.getElementById("new-tags");

function checkerror(json) {
  if(json["result"] == "error") {
    alert(json["res-text"]);
  }
}

function afteradd(json) {
  if(json["result"] == "error") {
    checkerror(json)
  } else {
    l.value = "";
    t.value = "";
    d.value = "";
    n.value = "";
    ta.value = "";
    t.placeholder = "title";
    d.placeholder = "detail";
  }
}

function add() {
  if(l.value == "" || t.value == "") {
    l.reportValidity();
    t.reportValidity();
    return
  }

  fetch("/api/bm/add?link="+encodeURIComponent(l.value)+"&note="+encodeURIComponent(n.value)+"&tags="+encodeURIComponent(ta.value)+"&detail="+encodeURIComponent(d.value)+"&title="+encodeURIComponent(t.value))
    .then((response) => response.json())
    .then((data) => afteradd(data));
}

function deletebm(bookmark) {
  if(confirm('really delete "'+bookmark.dataset.title+'" ?')) {
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
  t.placeholder = "title";
  d.placeholder = "detail";
  t.value = "";
  d.value = "";
}

function setlinkinfo(data) {
  t.value = data["title"];
  if(data["detail"] == "") {
    d.value = data["detail"];
    d.placeholder = "couldn't fetch detail";
  } else {
    d.value = data["detail"];
  }
}

function getlinkinfo() {
  if(l.value == "") {
    l.reportValidity();
    return
  }

  if(! /^http/.test(l.value)) {
    return
  }

  t.placeholder = "fetching title...";
  d.placeholder = "fetching detail...";

  fetch("/api/bm/linkinfo?link="+encodeURIComponent(l.value))
    .then((response) => response.json())
    .then((data) => setlinkinfo(data));
}

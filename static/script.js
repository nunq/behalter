"use strict";

const l = document.getElementById("new-link");
const t = document.getElementById("new-title");
const d = document.getElementById("new-detail");
const n = document.getElementById("new-note");
const ta = document.getElementById("new-tags");

// init tags autocomplete for ad dialog
edittagsfetch(ta);

function checkerror(json) {
  if(json["result"] == "error") {
    alert(json["res-text"]);
  }
}

function afteradd(json) {
  if(json["result"] == "error") {
    checkerror(json);
  } else {
    l.value = "";
    t.value = "";
    d.value = "";
    n.value = "";
    ta.value = "";
    t.placeholder = "title";
    d.placeholder = "detail";
    document.getElementById("wrapper").insertAdjacentHTML("afterbegin", json["bmhtml"]);
  }
}

function add() {
  if(l.value == "" || t.value == "") {
    l.reportValidity();
    t.reportValidity();
    return;
  }

  fetch("/api/bm/add?link="+encodeURIComponent(l.value)+"&note="+encodeURIComponent(n.value)+"&tags="+encodeURIComponent(ta.value)+"&detail="+encodeURIComponent(d.value)+"&title="+encodeURIComponent(t.value))
    .then((response) => response.json())
    .then((data) => afteradd(data));
}

function afterdel(json, ref) {
  if(json["result"] == "error") {
    checkerror(json);
  } else {
    document.getElementById("wrapper").removeChild(ref.parentElement.parentElement);
  }
}

function deletebm(ref) {
  if(confirm('really delete "'+ref.dataset.title+'" ?')) {
    fetch("/api/bm/delete?id="+ref.dataset.id)
      .then((response) => response.json())
      .then((data) => afterdel(data, ref));
  }
}

function edittags(json, ref) {
  if(json["result"] == "error") {
    checkerror(json);
  } else {
    ref.dataset.list = json["tags"].toString();
    new Awesomplete(ref, {
      filter: function(text, input) {
        return Awesomplete.FILTER_CONTAINS(text, input.match(/[^,]*$/)[0]);
      },

      item: function(text, input) {
        return Awesomplete.ITEM(text, input.match(/[^,]*$/)[0]);
      },

      replace: function(text) {
        var before = this.input.value.match(/^.+,\s*|/)[0];
        this.input.value = before + text + ", ";
      }
    });
  }
}

function edittagsfetch(ref) {
  // already initialized
  if(ref.parentElement.classList.contains("awesomplete")) {
    return;
  }
  fetch("/api/tags/get")
    .then((response) => response.json())
    .then((data) => edittags(data, ref));
}

function afteredit(json, ref) {
  if(json["result"] == "error") {
    checkerror(json);
  } else {
    for (var i=0; i<ref.parentElement.children.length-1; i++) {
      ref.parentElement.children[i].contentEditable = false;
      ref.parentElement.children[i].classList.remove("editing")
    }

    ref.parentElement.children[3].classList.remove("tagsediting");
    ref.parentElement.children[3].classList.add("tags");
    for (var i=0; i<ref.parentElement.children[3].children.length; i++) {
      ref.parentElement.children[3].children[i].setAttribute("onclick", "filterbytag(this)");
      ref.parentElement.children[4].children[0].setAttribute("onclick", "startedit(this)");
    }
    // remove button
    ref.parentElement.removeChild(ref.parentElement.lastChild);
  }
}

function sendedit(ref) {
  let e_title = ref.parentElement.children[0].innerText;
  let e_detail = ref.parentElement.children[1].innerText;
  let e_note = ref.parentElement.children[2].innerText;
  let e_tags = ref.parentElement.children[3].innerText;
  let bm_id = ref.parentElement.children[4].children[1].dataset.id;

  if(e_title.value == "") {
    return;
  }

  fetch("/api/bm/edit?id="+encodeURIComponent(bm_id)+"&note="+encodeURIComponent(e_note)+"&tags="+encodeURIComponent(e_tags)+"&detail="+encodeURIComponent(e_detail)+"&title="+encodeURIComponent(e_title))
    .then((response) => response.json())
    .then((data) => afteredit(data, ref));
}

function startedit(ref) {
  // -1 because meta section shouldnt be editable
  for (var i=0; i<ref.parentElement.parentElement.children.length-2; i++) {
    ref.parentElement.parentElement.children[i].contentEditable = true;
    ref.parentElement.parentElement.children[i].classList.add("editing")
  }

  // tags section needs special styling
  ref.parentElement.parentElement.children[3].classList.remove("tags");
  ref.parentElement.parentElement.children[3].classList.add("tagsediting");
  for (var i=0; i<ref.parentElement.parentElement.children[3].children.length; i++) {
    ref.parentElement.parentElement.children[3].children[i].removeAttribute("onclick");
    ref.removeAttribute("onclick");
  }
  var inner = ref.parentElement.parentElement.children[3].innerText;
  ref.parentElement.parentElement.children[3].innerHTML = "<input type='text' onfocusin='edittagsfetch(this)' value='"+inner.replaceAll(" ", ",")+"'>";

  ref.parentElement.parentElement.innerHTML += '<button onclick="sendedit(this)">submit</button>'
}

function filterbytag(tag) {
  window.location.href = "/search?tag="+encodeURIComponent(tag.innerHTML);
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
    return;
  }

  if(! /^http/.test(l.value)) {
    return;
  }

  t.placeholder = "fetching title...";
  d.placeholder = "fetching detail...";

  fetch("/api/bm/linkinfo?link="+encodeURIComponent(l.value))
    .then((response) => response.json())
    .then((data) => setlinkinfo(data));
}

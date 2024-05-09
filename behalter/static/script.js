"use strict";

const l = document.getElementById("new-link");
const t = document.getElementById("new-title");
const d = document.getElementById("new-detail");
const n = document.getElementById("new-note");
const ta = document.getElementById("new-tags");

// init tags autocomplete for add dialog
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

  fetch("/api/bm/add?link="+encodeURIComponent(l.value)+"&note="+encodeURIComponent(n.value)+"&tags="+encodeURIComponent(ta.value.replace(/, *$/, ""))+"&detail="+encodeURIComponent(d.value)+"&title="+encodeURIComponent(t.value))
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
    ref.parentElement.outerHTML = json["bmhtml"];
  }
}

function sendedit(ref) {
  let e_title = ref.parentElement.children[0].innerText;
  let e_detail = ref.parentElement.children[1].innerText;
  let e_note = ref.parentElement.children[2].innerText;
  let bm_id = ref.parentElement.children[4].children[1].dataset.id;

  if(ref.parentElement.children[3].children[0].value === undefined) {
    // tags were edited
    var e_tags_pre = ref.parentElement.children[3].children[0].children[0].value;
  } else if(ref.parentElement.children[3].children[0].children[0] === undefined) {
    // tags were not edited
    var e_tags_pre = ref.parentElement.children[3].children[0].value;
  }

  let e_tags = e_tags_pre.replace(/, *$/, "").replace(/, */, ",");

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
    ref.parentElement.parentElement.children[i].classList.add("editing");
  }

  // tags section needs special styling
  ref.parentElement.parentElement.children[3].classList.remove("tags");
  ref.parentElement.parentElement.children[3].classList.add("tagsediting");
  for (var i=0; i<ref.parentElement.parentElement.children[3].children.length; i++) {
    ref.parentElement.parentElement.children[3].children[i].removeAttribute("onclick");
    ref.removeAttribute("onclick");
  }
  var inner = ref.parentElement.parentElement.children[3].innerText;
  ref.parentElement.parentElement.children[3].innerHTML = "<input type='text' onclick='edittagsfetch(this)' value='"+inner.replaceAll(" ", ",")+"'>";

  //ref.parentElement.insertAdjacentHTML("beforebegin", '<label style="font-size: 16px;"><input type="checkbox" id="usearchive">use archive</label>');
  ref.parentElement.parentElement.innerHTML += '<button onclick="sendedit(this)">submit</button>';

}

function filterbytag(tag) {
  window.location.href = "/search?q=tag:"+encodeURIComponent(tag.innerText);
}

function resetfields() {
  t.placeholder = "title";
  d.placeholder = "detail";
  t.value = "";
  d.value = "";
}

function setlinkinfo(data) {
  t.value = data["title"];
  d.value = data["detail"];

  if(data["title"] == "") {
    t.placeholder = "couldn't fetch title";
  }

  if(data["detail"] == "") {
    d.placeholder = "couldn't fetch detail";
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

document.body.addEventListener("keydown", function(e) {
  if(!(e.keyCode == 13 && e.ctrlKey)) return;
  add();
});

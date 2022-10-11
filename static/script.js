function send() {
  // TODO validation
  s = document.getElementById("new-link").value;
  n = document.getElementById("new-note").value;
  t = document.getElementById("new-tags").value;

  fetch("/api/add?source="+encodeURIComponent(s)+"&note="+encodeURIComponent(n)+"&tags="+encodeURIComponent(t))
    .then((response) => response.json())
    .then((data) => console.log(data));
}

function get_link_info() {
  l = document.getElementById("new-link").value;

  fetch("/api/linkinfo?link="+encodeURIComponent(l))
    .then((response) => response.json())
    .then((data) => console.log(data));
}

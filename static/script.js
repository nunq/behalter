function send() {
  // TODO validation
  l = document.getElementById("new-link").value;
  t = document.getElementById("new-title").value;
  d = document.getElementById("new-description").value;
  n = document.getElementById("new-note").value;
  ta = document.getElementById("new-tags").value;

  fetch("/api/add?link="+encodeURIComponent(l)+"&note="+encodeURIComponent(n)+"&tags="+encodeURIComponent(ta)+"&description="+encodeURIComponent(d)+"&title="+encodeURIComponent(t))
    .then((response) => response.json())
    .then((data) => console.log(data));
}

function get_link_info() {
  l = document.getElementById("new-link").value;

  fetch("/api/linkinfo?link="+encodeURIComponent(l))
    .then((response) => response.json())
    .then((data) => console.log(data));
}

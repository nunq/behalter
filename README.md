# behalter

simple bookmarks management

note: archive feature not yet implemented

## setup

* create a new user on your server (the config files use the user `behalter`)
* copy files to server (and customize the service config files)
* create your bookmarks database using the schema file:
  `sqlite3 bm.db < schema.sql`
* install pip dependencies
* make sure the unix socket is properly set up
* adjust your nginx config, do the `uwsgi_pass` to your unix socket
* optionally add http basic auth (behalter doesnt do any auth by itself)
* restart nginx
* start the provided systemd service file
* everything should work

the site itself uses an [experimental new css setting](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Masonry_Layout) to automatically show the bookmarks as cards side by side.

as of now it's only implemented in firefox and hidden behind a flag, see [caniuse](https://caniuse.com/mdn-css_properties_grid-template-rows_masonry)

in firefox' about:config set `layout.css.grid-template-masonry-value.enabled` to `true`

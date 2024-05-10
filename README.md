# behalter

simple bookmarks management

## features
* auto-fetches link and detail for url
* add personal note to each bookmark
* tagging, with auto-suggestions
* search by query
* search by tag (using 'tag:...' in the search bar)
* search by id (using 'id:...' in the search bar)
* duplicate detection
* edit & delete bookmarks
* uses just an sqlite database

## setup
* customize the http basic auth settings in behalter.nix
* add the contents of behalter.nix to your nix config
* cp the files to /var/lib/behalter/
* chown to uwsgi:uwsgi
* rebuild nix
* restart uwsgi

## screenshot
the colorscheme is supposed to resemble a pinboard with post-its.

![screenshot of the behalter web ui](./screenshot.png)

## notes
the site itself uses an [experimental new css setting](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout/Masonry_Layout) to automatically show the bookmarks as cards side by side.

as of now it's only implemented in firefox and hidden behind a flag, see [caniuse](https://caniuse.com/mdn-css_properties_grid-template-rows_masonry)

in firefox' about:config set `layout.css.grid-template-masonry-value.enabled` to `true`

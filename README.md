# JukeBox

## Developing

### Get it running
- git clone https://github.com/armooo/jukebox.git
- virtualenv --system-site-packages venv #  to use a system pygst
- . env/bin/activate
- pip install -e .
- npm install .
- grunt
- twistd -n web --class=jukebox.config.resource

If you are using the GSTEncoder you need to use the glib2 integration reactor
by passing -r glib2 to twistd.

### Running tests etc
- pip install -r dev\_requirements.txt
- py.test -f
- grunt watch-test

Both py.test and grunt will stay running and retun the tests when the files
change. Grunt will also redeploy the JS  and CSS.

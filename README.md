# JukeBox

## Developing

### Get it running
- git clone https://github.com/armooo/jukebox.git
- virtualenv venv
- . env/bin/activate
- pip install -e .
- npm install .
- grunt
- twistd -n web --class=jukebox.resource

### Running tests etc
- pip install -r dev\_requirements.txt
- py.test -f
- grunt watch-test

Both py.test and grunt will stay running and retun the tests when the files
change. Grunt will also redeploy the JS  and CSS.

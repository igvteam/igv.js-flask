import os
from igvjs import app

port = int(os.environ.get('PORT', 5000))
host = '127.0.0.1' if app.config['DEBUG'] else '0.0.0.0'
app.run(port=port, host=host)

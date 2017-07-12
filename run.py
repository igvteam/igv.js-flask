import os
from igvjs import app

port = int(os.environ.get('PORT', 5000))
app.run(port=port, host='0.0.0.0')

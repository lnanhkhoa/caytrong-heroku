import os
import client

port = os.getenv('PORT', '5000')
host = '0.0.0.0'

if __name__ == "__main__":
    client.app.run(host=host, port=int(port), debug=True, threaded=True)
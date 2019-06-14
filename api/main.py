from sanic import Sanic
from sanic_cors import CORS, cross_origin
from services import kube
from router import routes

app = Sanic()
app.config['CORS_AUTOMATIC_OPTIONS'] = True
CORS(app, resources={r"/*": {"origins": "*"}})

kube.init()
routes.add_routes(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
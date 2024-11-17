from flask import Blueprint

chat = Blueprint("chat", __name__)
webgal = Blueprint("webgal", __name__, url_prefix='/webgal')


from . import routes, orm, webgal_routes

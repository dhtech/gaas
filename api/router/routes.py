from sanic.response import json, text
from sanic.exceptions import ServerError
from services import servers
from games import enabled
from router.limit import allowed_client

ALLOWED_CLIENTS=["77.80.128.0/17", "172.17.0.0/24"] # DH and local Docker

def add_routes(app):
    app.add_route(addServer, '/servers/<game_id>', methods=['POST'])
    app.add_route(deleteServer, '/servers/<uid>', methods=['DELETE'])
    app.add_route(getServer, '/servers', methods=['GET'])
    app.add_route(getGames, '/games', methods=['GET'])
    app.add_route(health, '/health', methods=['GET'])


async def addServer(request, game_id):
    if not allowed_client(request.ip, ALLOWED_CLIENTS):
        raise ServerError("Client is not allowed")
    try:
        return json(servers.add(request.ip, game_id, request.json))
    except Exception as e:
        raise ServerError(e)

async def deleteServer(request, uid):
    if not allowed_client(request.ip, ALLOWED_CLIENTS):
        raise ServerError("Client is not allowed")
    try:
        return json(servers.delete(uid, request.ip))
    except Exception as e:
        raise ServerError(e)

async def getServer(request):
    if not allowed_client(request.ip, ALLOWED_CLIENTS):
        raise ServerError("Client is not allowed")
    try:
        return json(servers.list(request.ip))
    except Exception as e:
        raise ServerError(e)


async def getGames(request):
    if not allowed_client(request.ip, ALLOWED_CLIENTS):
        raise ServerError("Client is not allowed")
    try:
        return json(enabled.get_enabled())
    except Exception as e:
        raise ServerError(e)


async def health(request):
    return text("Nice!")

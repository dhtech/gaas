from games.specs.nginx import NginxGameSpec
from games.specs.csgo import CSGoGameSpec
from games.specs.css import CSSGameSpec
from games.specs.factorio import FactorioGameSpec

ENABLED_GAMES={
    CSSGameSpec.id: CSSGameSpec(),
    CSGoGameSpec.id: CSGoGameSpec(),
    FactorioGameSpec.id: FactorioGameSpec()
}

def get_enabled():
    return ENABLED_GAMES

def get_game_by_id(game_id):
    if game_id not in ENABLED_GAMES:
        raise Exception("GameID {} not found.".format(game_id))
    return ENABLED_GAMES[game_id]

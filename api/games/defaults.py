class GameSpec(object):

    id=""
    name=""
    params=[]

    def __init__(self):
        if len(self.name) < 2:
            raise Exception("Game names must be at least 2 characters.")
        if len(self.id) < 2:
            raise Exception("GameID must be at least 2 characters.")
        for param in self.params:
            if not isinstance(param, Param):
                raise Exception("Invalid param for game {}.".format(self.name))
            if param.id not in self.get_param_constraints():
                raise Exception("Missing constraints for {}.".format(param.id))
        if not self.make_deployment:
            raise Exception("Missing deployment spec for {}.".format(self.name))
        if not self.make_service:
            raise Exception("Missing deployment spec for {}.".format(self.name))

    def validate_params(self, params):
        constrainsts = self.get_param_constraints()
        expected={p.id: constrainsts[p.id] for p in self.params}
        for key, value in params.items():
            if key not in expected:
                raise Exception("Unexpected parameter {}.".format(key))
            for check, message in expected[key]:
                if not check(value):
                    raise Exception(message)

        for p in self.params:
            if not p.optional:
                if p.id not in params:
                    raise Exception("Missing parameter {}.".format(key))
        return True
    
    def get_param_constraints(self):
        return {}


class ParamTypes(object):
    INT="int"
    STRING="string"
    TYPES=[INT, STRING]


class Param(object):

    def __init__(self, id, type, name, description, optional=False, default=None):
        if type not in ParamTypes.TYPES:
            raise Exception("Param type {} is not valid.".format(type))
        
        self.id=id
        self.type=type
        self.name=name
        self.description=description
        self.default=default
        self.optional=optional


class ParamException(Exception):
    pass
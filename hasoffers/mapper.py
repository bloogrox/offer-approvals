class Model(object):

    def __init__(self, d):
        for k, v in d.items():
            if k == 'id':
                self.__dict__[k] = int(v)
            else:
                self.__dict__[k] = v


class Mapper(object):

    @classmethod
    def extract_one(cls, data, model_name):

        if not len(data):
            return None

        relative_scopes = {model: scope
                           for model, scope in data.items()
                           if model != model_name}
        model_scope = data[model_name]
        model_scope.update(relative_scopes)
        model = Model(model_scope)

        return model

    @classmethod
    def extract_all(cls, data, model_name):

        if not len(data):
            return []

        collection = []

        for object_id, object_scope in data.items():
            relative_scopes = {model: scope
                               for model, scope in object_scope.items()
                               if model != model_name}
            model_scope = object_scope[model_name]
            model_scope.update(relative_scopes)

            model = Model(model_scope)

            collection.append(model)

        return collection

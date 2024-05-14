from frost_sta_client.model import location
class Location(location.Location):
    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
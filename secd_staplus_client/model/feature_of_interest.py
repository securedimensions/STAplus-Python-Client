from frost_sta_client.model import feature_of_interest
class FeatureOfInterest(feature_of_interest.FeatureOfInterest):
    def clone(self):
        entity = self.__class__()
        entity.id = self.id
        return entity
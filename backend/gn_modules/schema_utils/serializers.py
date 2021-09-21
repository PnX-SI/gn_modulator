'''
    SchemaMethods : serializers

    ?? que faire 
      - SchemaMarshmallow
      - as_dict, from_dict sqlalchemy
      - custom 
'''

class SchemaSerializers:
    '''
        schema model serializer class

        TODO
    '''
    def serialize(self, r):
        '''
            TODO 
        '''
        return {
            k: getattr(r, k)
            for k, v in self.properties(processed_properties_only=True).items()
        }

    def unserialize(self, m, data):
        '''
            TODO
        '''
        for k, v in data.items():
            if hasattr(m, k):
                setattr(m, k, data[k])


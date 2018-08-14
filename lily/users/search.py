from lily.search.base_mapping import BaseMapping

from .models import LilyUser, Team


class LilyUserMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return LilyUser

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(LilyUserMapping, cls).get_mapping()
        mapping['properties'].update({
            'first_name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'last_name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'full_name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'position': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'is_active': {
                'type': 'boolean',
            },
            'email': {
                'type': 'string',
                'analyzer': 'email_analyzer',
            },
            'phone_number': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
            'internal_number': {
                'type': 'integer',
                'index_analyzer': 'simple',
            },
            'teams': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer'
                    },
                    'name': {
                        'type': 'string',
                        'analyzer': 'normal_edge_analyzer',
                    },
                },
            },
        })
        return mapping

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'full_name': obj.full_name,
            'position': obj.position,
            'profile_picture': obj.profile_picture,
            'email': obj.email,
            'is_active': obj.is_active,
            'is_admin': obj.is_admin,
            'phone_number': obj.phone_number,
            'internal_number': obj.internal_number,
            'teams': [{
                'id': team.id,
                'name': team.name,
            } for team in obj.teams.all()],
        }


class TeamMapping(BaseMapping):
    @classmethod
    def get_model(cls):
        return Team

    @classmethod
    def get_mapping(cls):
        """
        Returns an Elasticsearch mapping for this MappingType.
        """
        mapping = super(TeamMapping, cls).get_mapping()
        mapping['properties'].update({
            'name': {
                'type': 'string',
                'index_analyzer': 'normal_ngram_analyzer',
            },
        })
        return mapping

    @classmethod
    def obj_to_doc(cls, obj):
        """
        Translate an object to an index document.
        """
        return {
            'name': obj.name,
        }

from django_filters import rest_framework as filters

from lily.users.models import Team, LilyUser


class TeamFilter(filters.FilterSet):
    """
    Class to filter case queryset.
    """

    class Meta:
        model = Team
        fields = ['name', ]


class LilyUserFilter(filters.FilterSet):
    class Meta:
        model = LilyUser
        fields = {
            'is_active': ['exact', ],
            'teams': ['isnull', ],
        }

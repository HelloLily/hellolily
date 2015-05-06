from lily.utils.api.serializers import RelatedModelSerializer
from ..models import Tag


class TagSerializer(RelatedModelSerializer):

    def create(self, validated_data):
        ModelClass = self.Meta.model
        validated_data['content_type'] = self.related_object.content_type
        validated_data['object_id'] = self.related_object.pk
        instance = ModelClass.objects.create(**validated_data)
        return instance

    class Meta:
        model = Tag
        fields = ('id', 'name',)

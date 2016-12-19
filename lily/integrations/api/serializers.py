from rest_framework import serializers

from lily.api.nested.mixins import RelatedSerializerMixin

from ..models import IntegrationDetails, Document


class IntegrationSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = IntegrationDetails
        fields = (
            'id',
            'type',
            'type_display',
        )


class RelatedIntegrationSerializer(RelatedSerializerMixin, IntegrationSerializer):
    pass


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = (
            'id',
            'contact',
            'deal',
            'document_id',
        )

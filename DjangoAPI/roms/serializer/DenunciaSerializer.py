from rest_framework import serializers
from roms.models import Denuncia

class DenunciaSerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Denuncia
        fields = [
            'id',
            'reported_by',
            'content_type',
            'content_type_name',
            'content_id',
            'reason',
            'status',
            'reviewed_by',
            'resolution',
            'created_at',
            'updated_at',
        ]

    def get_content_type_name(self, obj):
        return obj.content_type.model
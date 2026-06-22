from rest_framework import serializers

class UploadCSVSerializer(serializers.Serializer):
    file = serializers.FileField()

class BatchRequestSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    batch = serializers.IntegerField()

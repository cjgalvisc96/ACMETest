from rest_framework import serializers


class ConditionSerializer(serializers.Serializer):
    from_id = serializers.CharField(max_length=50)
    field_id = serializers.CharField(max_length=50)
    operator = serializers.CharField(max_length=50)
    value = [serializers.BooleanField(), serializers.FloatField()]


class TransitionSerializer(serializers.Serializer):
    condition = ConditionSerializer(many=True)
    target = serializers.CharField(max_length=50)


class StepSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=50)
    params = serializers.DictField()
    action = serializers.CharField(max_length=50)
    transitions = TransitionSerializer(many=True)


class TriggerSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=50)
    params = serializers.DictField()
    transitions = TransitionSerializer(many=True)


class WorkflowSerializer(serializers.Serializer):
    steps = StepSerializer(many=True)
    trigger = TriggerSerializer()

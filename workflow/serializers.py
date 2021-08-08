from rest_framework import serializers


class ConditionSerializer(serializers.Serializer):
    from_id = serializers.CharField(max_length=200)
    field_id = serializers.CharField(max_length=200)
    operator = serializers.CharField(max_length=200)
    value = [serializers.BooleanField(), serializers.FloatField()]


class TransitionSerializer(serializers.Serializer):
    condition = ConditionSerializer(many=True)
    target = serializers.CharField(max_length=200)


class StepSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=200)
    params = serializers.DictField()
    action = serializers.CharField(max_length=200)
    transitions = TransitionSerializer(many=True)


class TriggerSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=200)
    params = serializers.DictField()
    transitions = TransitionSerializer(many=True)


class WorkflowSerializer(serializers.Serializer):
    steps = StepSerializer(many=True)
    trigger = TriggerSerializer()

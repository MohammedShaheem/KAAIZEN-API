from rest_framework import serializers
from trainers.models import TrainerProfile
from trainers.choices import Skill

class TrainerProfileSerializer(serializers.ModelSerializer):
    skills = serializers.ListField(
        child=serializers.ChoiceField(choices=Skill.choices),
        allow_empty=True,
        required=False
    )

    class Meta:
        model = TrainerProfile
        exclude = ['user']
        read_only_fields = (
            'created_at',
            'updated_at',
        )

    def validate_skills(self, value):
        #ensuring no duplicates
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate skills are not allowed.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        if user.role != 'trainer':
            raise serializers.ValidationError("Only trainers can create profiles.")
        return TrainerProfile.objects.create(user=user, **validated_data, is_verified=False)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
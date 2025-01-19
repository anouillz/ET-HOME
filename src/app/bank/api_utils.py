from rest_framework import serializers
from django.db import models

def to_json(obj,model,many=False):
    return UniversalSerializer(obj,model=model,many=many,safe=False).data

class UniversalSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        model = kwargs.pop('model', None)  # Get model from kwargs
        super().__init__(*args, **kwargs)

        if model:
            self.Meta.model = model
            self.Meta.fields = '__all__'  # Include all fields dynamically

            # Convert ForeignKey and ManyToMany fields to show only ID
            for field_name, field in model._meta.fields_map.items():
                if isinstance(field, models.ForeignKey):
                    self.fields[field_name] = serializers.PrimaryKeyRelatedField(
                        queryset=field.related_model.objects.all()
                    )
                elif isinstance(field, models.ManyToManyField):
                    self.fields[field_name] = serializers.PrimaryKeyRelatedField(
                        queryset=field.related_model.objects.all(),
                        many=True
                    )

    class Meta:
        model = None
        fields = '__all__'
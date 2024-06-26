"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects."""

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for the recipe object."""
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'title', 'time_minutes', 'price', 'link',
            'description', 'tags'
        )
        read_only_fields = ('id',)

    # override the create method to handle the tags
    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, _ = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipe.tags.add(tag_obj)
        return recipe


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail object."""

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields

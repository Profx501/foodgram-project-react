import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    User,
    RecipeIngredient,
    ShoppingList,
    Favorite,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return False


class IngredientAmountSerializer(serializers.ModelSerializer):

    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        ingredients = RecipeIngredient.objects.filter(ingredient=obj)
        return ingredients[0].amount


class RecipeInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipelistSerializer(serializers.ModelSerializer):

    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):

    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                recipe=recipe,
                amount=ingredient.get('amount'),
            )
        return recipe

    def create_or_update_ingredients(self, ingredients, instance):
        ingredient_ids = []
        for ingredient in ingredients:
            ingredient_instance, _ = RecipeIngredient.objects.update_or_create(
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                recipe=instance,
                amount=ingredient.get('amount'),
                defaults=ingredient,
            )
            ingredient_ids.append(ingredient_instance.pk)
        return ingredient_ids

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        if 'tags' in validated_data:
            instance.tags.set(validated_data.get('tags'))
        if 'ingredients' in validated_data:
            ingredient = validated_data.pop('ingredients', [])
            instance.ingredients.set(
                self.create_or_update_ingredients(
                    ingredient,
                    instance,
                )
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        if isinstance(instance, Recipe):
            serializer = RecipelistSerializer(instance)
        return serializer.data


class ShoppingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingList
        fields = (
            'user',
            'recipe',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingList.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен!'

            )
        ]


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен!'

            )
        ]

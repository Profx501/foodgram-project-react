import base64

from djoser.serializers import UserSerializer as DjoserUserSerializer
from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
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
    Follow,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class UserSerializer(DjoserUserSerializer):
    """Сериализатор для модели User."""
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
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.follower.filter(following=obj).exists()


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор с полем amount."""
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_amount(self, obj):
        ingredients = RecipeIngredient.objects.filter(ingredient=obj)
        return ingredients[0].amount


class RecipeInfoSerializer(serializers.ModelSerializer):
    """Сериализатор для частичной отображения информации о Recipe."""
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class RecipelistSerializer(serializers.ModelSerializer):
    """Сериализатор для Recipe GET."""
    tags = TagSerializer(read_only=True, many=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_list.filter(recipe=obj).exists()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиентов."""
    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для Recipe POST."""
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

    def validate(self, data):
        ingredient_ids = []
        tags_ids = []
        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError('Пустое поля tags!!')
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError('Пустое поля ingredients!!')
        for ingredient in ingredients:
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError(
                    'Кол-во ингредиентов меньше 1'
                )
            if ingredient.get('id') not in ingredient_ids:
                ingredient_ids.append(ingredient.get('id'))
            else:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться!!'
                )
        for tag in tags:
            if tag not in tags_ids:
                tags_ids.append(tag)
            else:
                raise serializers.ValidationError(
                    'Теги не должны повторяться!!'
                )
        return data

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            try:
                RecipeIngredient.objects.create(
                    ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                    recipe=recipe,
                    amount=ingredient.get('amount'),
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    'Указан не существующий ингредиент!'
                )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time,
        )
        instance.tags.set(validated_data.get('tags'))
        ingredients = validated_data.pop('ingredients', [])
        for ingredient in ingredients:
            try:
                RecipeIngredient.objects.update(
                    ingredient=Ingredient.objects.get(
                        pk=ingredient.get('id')
                    ),
                    recipe=instance,
                    amount=ingredient.get('amount'),
                )
            except ObjectDoesNotExist:
                raise serializers.ValidationError(
                    'Указан не существующий ингредиент!'
                )
        instance.save()
        return instance

    def to_representation(self, instance):
        if isinstance(instance, Recipe):
            serializer = RecipelistSerializer(instance)
        return serializer.data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для модели ShoppingList."""
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
    """Сериализатор для модули Favorite."""
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


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
    class Meta:
        model = Follow
        fields = (
            'user',
            'following',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны!!!',
            )
        ]

    def validate(self, data):
        if data.get('user') == data.get('following'):
            raise serializers.ValidationError('Нельзя подписаться на себя!!!')
        return data


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для отображения списка покупок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        recipe_author = obj.recipe.all()
        if recipes_limit is not None:
            recipe_author = obj.recipe.all()[:int(recipes_limit)]
        info_recipe = RecipeInfoSerializer(recipe_author, many=True)
        return info_recipe.data

    def get_recipes_count(self, obj):
        return obj.recipe.count()

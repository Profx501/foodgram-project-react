from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Tag, Ingredient, Recipe, ShoppingList, Favorite
from .serializers import (
    TagSerializer,
    IngredientSerializer,
    RecipelistSerializer,
    RecipeSerializer,
    ShoppingListSerializer,
    RecipeInfoSerializer,
    FavoriteSerializer,
)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'delete', 'patch']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipelistSerializer
        return RecipeSerializer

    @action(
        ['POST', 'DELETE'],
        detail=True,
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingListSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            recipe_shopping_cart_serializer = RecipeInfoSerializer(recipe)
            return Response(
                data=recipe_shopping_cart_serializer.data,
                status=status.HTTP_201_CREATED,

            )
        shopping_cart = get_object_or_404(
            ShoppingList,
            user=request.user,
            recipe=recipe,
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['POST', 'DELETE'],
        detail=True,
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            recipe_favorite_serializer = RecipeInfoSerializer(recipe)
            return Response(
                data=recipe_favorite_serializer.data,
                status=status.HTTP_201_CREATED,
            )
        favorite = get_object_or_404(
            Favorite,
            user=request.user,
            recipe=recipe
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from django.contrib import admin

from .models import (
    Tag,
    Recipe,
    Ingredient,
    RecipeIngredient,
    Follow,
    ShoppingList,
    Favorite,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = (
        'name',
        'color',
        'slug',
    )

    list_per_page = 10
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeIngredientInline(admin.StackedInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'author',
        'count_favorite',
    )
    inlines = (RecipeIngredientInline, )

    list_filter = ('author', 'name', 'tags')
    list_per_page = 10
    search_fields = ('author', 'name')

    def count_favorite(self, object):
        return object.favorite.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )

    list_filter = ('name',)
    list_per_page = 10
    search_fields = ('name',)
    ordering = ('pk',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_editable = (
        'user',
        'recipe',
    )

    list_filter = ('user',)
    search_fields = ('user',)
    list_per_page = 10


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'recipe',
    )
    list_editable = (
        'user',
        'recipe',
    )

    list_filter = ('user',)
    search_fields = ('user',)
    list_per_page = 10


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'recipe',
        'ingredient',
        'amount',
    )

    list_per_page = 10


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'user',
        'following',
    )

    list_per_page = 10

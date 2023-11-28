from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()


class Tag(models.Model):
    """Модель для хранения информации о тэге."""
    name = models.CharField(
        verbose_name='Название Тэга',
        max_length=150,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цвет',
        max_length=25,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=150,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ('name',)

    def __str__(self):
        return f'Тэг: {self.name}'


class Ingredient(models.Model):
    """Модель для хранения информации о ингредиенте."""
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=150,
        unique=True,
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=150,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} в {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для хранения информации о рецепте."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор',
    )
    name = models.CharField(verbose_name='Название рецепта', max_length=200)
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipe/images/'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipe',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('pub_date',)

    def __str__(self):
        return f'Рецепт: {self.name}'


class RecipeIngredient(models.Model):
    """Промежуточная модель для хранения ключей recipe, ingredient и кол-во."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Ингредиент',
    )
    amount = models.FloatField(
        verbose_name='Кол-во',
        validators=(
            MinValueValidator(
                0.5,
                message='Минимальное количество ингредиентов!',
            ),
        )

    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'

    def __str__(self):
        return f'{self.recipe} -> {self.ingredient}'


class Follow(models.Model):
    """Модель для хранения информации о подписках."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='Unique_follow'
            ),
        )

    def __str__(self):
        return f'Пользователь: {self.user} подписан на {self.following}'


class ShoppingList(models.Model):
    """Модель для хранения информации о купленных рецептах."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата покупки',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        default_related_name = 'shopping_list'
        ordering = ('pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Unique_ShoppingList'
            ),
        )

    def __str__(self):
        return f'Пользователь: {self.user} купил {self.recipe}'


class Favorite(models.Model):
    """Модель для хранения информации о избранных рецептах."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        default_related_name = 'favorite'
        ordering = ('pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='Unique_Favorite'
            ),
        )

    def __str__(self):
        return f'Пользователь: {self.user} добавил {self.recipe}'

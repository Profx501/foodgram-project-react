from django.contrib import admin

from .models import User

admin.site.site_header = 'Администрирование Foodgram'
admin.site.index_title = 'Администрирование сайта Foodgram'
admin.site.empty_value_display = 'Не задано'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_editable = (
        'username',
        'email',
        'first_name',
        'last_name',
    )

    list_per_page = 10
    list_filter = ('email', 'username')

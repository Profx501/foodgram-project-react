import csv

from django.db.utils import IntegrityError
from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует данные из csv-файлов в базу данных'

    def handle(self, *args, **options):
        with open(
            f'{settings.DATA_DIR}/ingredients.csv',
            encoding='utf-8'
        ) as csv_file:
            reader = csv.reader(csv_file)
            next(reader)
            for row in reader:
                try:
                    Ingredient.objects.create(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                except IntegrityError:
                    continue
            self.stdout.write(
                self.style.SUCCESS('Данные успешно импортированы')
            )

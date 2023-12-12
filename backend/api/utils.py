from django.conf import settings
from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_pdf(ingredient_list):
    """Создает и заполняет pdf file."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'
    pdfmetrics.registerFont(
        TTFont(
            'Times',
            f'{settings.BASE_DIR}/fonts/timesnewromanpsmt.ttf',
            'UTF-8',
        )
    )
    p = canvas.Canvas(response)
    p.setFont('Times', settings.FONT)
    p.drawString(
        settings.STRING_TITLE_X,
        settings.STRING_TITLE_Y,
        'Список Ингредиентов.',
    )
    y = settings.STRING_CONTENT_Y
    for ingredient in ingredient_list:
        p.drawString(
            settings.STRING_CONTENT_X,
            y,
            f"{ingredient['total_amount']} "
            f"{ingredient['recipe__ingredients__measurement_unit']}.  "
            f"{ingredient['recipe__ingredients__name']};",
        )
        y -= settings.LINE_OFFSET_CONTENT
    p.showPage()
    p.save()
    return response

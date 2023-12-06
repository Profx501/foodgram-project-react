from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def get_pdf(ingredient_list):
    """Создает и заполняет pdf file."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="file.pdf"'
    pdfmetrics.registerFont(TTFont('Times', 'times.ttf', 'UTF-8'))
    p = canvas.Canvas(response)
    p.setFont('Times', 25)
    p.drawString(150, 800, 'Список Ингредиентов.')
    y = 750
    for ingredient in ingredient_list:
        p.drawString(
            50,
            y,
            f"{ingredient['total_amount']} "
            f"{ingredient['recipe__ingredients__measurement_unit']}.  "
            f"{ingredient['recipe__ingredients__name']};",
        )
        y -= 25
    p.showPage()
    p.save()
    return response

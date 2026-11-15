from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from .models import Transaction

CHARCOAL = HexColor('#1B1818')
GOLD = HexColor('#B9975C')
IVORY = HexColor('#F7F3EE')


@login_required
def invoice_pdf(request, pk):
    tx = get_object_or_404(Transaction.objects.select_related('customer', 'cashier'), pk=pk)
    if not request.user.has_role('ADMIN') and not request.user.has_role('CASHIER'):
        return HttpResponse('Unauthorized', status=403)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice-{}.pdf"'.format(tx.transaction_number)

    c = canvas.Canvas(response, pagesize=A4)
    w, h = A4

    # Header branding
    c.setFillColor(CHARCOAL)
    c.rect(0, h - 40 * mm, w, 30 * mm, stroke=0, fill=1)
    c.setFillColor(HexColor('#F7F3EE'))
    c.setFont('Helvetica-Bold', 20)
    c.drawString(20 * mm, h - 20 * mm, 'VELOURA')
    c.setFont('Helvetica', 9)
    c.drawString(20 * mm, h - 27 * mm, 'Fashion Management System  |  Sales Invoice')
    c.setFillColor(GOLD)
    c.setFont('Helvetica-Bold', 12)
    c.drawRightString(w - 20 * mm, h - 20 * mm, 'INVOICE')
    c.setFillColor(HexColor('#8A8A8A'))
    c.setFont('Helvetica', 9)
    c.drawRightString(w - 20 * mm, h - 27 * mm, tx.transaction_number)

    c.setFillColor(CHARCOAL)
    y = h - 55 * mm
    c.setFont('Helvetica-Bold', 9)
    c.drawString(20 * mm, y, 'Invoice No:')
    c.drawString(70 * mm, y, tx.transaction_number)
    c.drawString(20 * mm, y - 6 * mm, 'Date:')
    c.drawString(70 * mm, y - 6 * mm, tx.transaction_date.strftime('%d %b %Y'))
    c.drawString(20 * mm, y - 12 * mm, 'Cashier:')
    c.drawString(70 * mm, y - 12 * mm, tx.cashier.username)
    c.drawString(20 * mm, y - 18 * mm, 'Customer:')
    c.drawString(70 * mm, y - 18 * mm, tx.customer.full_name if tx.customer else 'Walk-in Customer')
    c.drawString(20 * mm, y - 24 * mm, 'Status:')
    c.drawString(70 * mm, y - 24 * mm, tx.get_status_display())

    y -= 42 * mm
    # Table header
    c.setFillColor(IVORY)
    c.rect(20 * mm, y, w - 40 * mm, 8 * mm, stroke=0, fill=1)
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 8.5)
    c.drawString(22 * mm, y + 2.5 * mm, 'Item')
    c.drawString(100 * mm, y + 2.5 * mm, 'SKU / Barcode')
    c.drawString(170 * mm, y + 2.5 * mm, 'Size / Color')
    c.drawRightString(w - 40 * mm, y + 2.5 * mm, 'Qty')
    c.drawRightString(w - 28 * mm, y + 2.5 * mm, 'Price')
    c.drawRightString(w - 12 * mm, y + 2.5 * mm, 'Total')
    y -= 8 * mm

    c.setFont('Helvetica', 8.5)
    for item in tx.items.all():
        c.setFillColor(CHARCOAL)
        c.drawString(22 * mm, y + 1.5 * mm, item.product_variant.product.name[:28])
        c.drawString(100 * mm, y + 1.5 * mm, item.product_variant.sku)
        c.drawString(170 * mm, y + 1.5 * mm, '{}/{}'.format(item.product_variant.get_size_display(), item.product_variant.color[:12]))
        c.drawRightString(w - 40 * mm, y + 1.5 * mm, str(item.quantity))
        c.drawRightString(w - 28 * mm, y + 1.5 * mm, '{:,.0f}'.format(item.unit_price))
        c.drawRightString(w - 12 * mm, y + 1.5 * mm, '{:,.0f}'.format(item.total))
        y -= 7 * mm
        if y < 40 * mm:
            c.showPage()
            y = h - 40 * mm

    # Totals
    c.setFillColor(IVORY)
    c.rect(20 * mm, y - 10 * mm, w - 40 * mm, 34 * mm, stroke=0, fill=1)
    c.setFillColor(CHARCOAL)
    c.setFont('Helvetica-Bold', 9)
    c.drawString(22 * mm, y - 7 * mm, 'Subtotal:')
    c.drawRightString(w - 12 * mm, y - 7 * mm, '{:,.0f}'.format(tx.subtotal))
    c.drawString(22 * mm, y - 13 * mm, 'Discount:')
    c.drawRightString(w - 12 * mm, y - 13 * mm, '-{:,.0f}'.format(tx.discount_amount))
    c.drawString(22 * mm, y - 19 * mm, 'Payment:')
    c.drawRightString(w - 12 * mm, y - 19 * mm, tx.get_payment_status_display())
    c.setFont('Helvetica-Bold', 13)
    c.drawString(22 * mm, y - 27 * mm, 'Grand Total:')
    c.drawRightString(w - 12 * mm, y - 27 * mm, '{:,.0f}'.format(tx.grand_total))

    c.setFillColor(HexColor('#8A8A8A'))
    c.setFont('Helvetica', 7.5)
    c.drawString(20 * mm, 15 * mm, 'VELOURA Fashion Management System  |  Thank you for your purchase.')
    c.drawString(20 * mm, 10 * mm, 'Stock is deducted only after payment is confirmed.')

    c.showPage()
    c.save()
    return response

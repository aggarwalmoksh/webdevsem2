import random
import string
import qrcode
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.flowables import Image
from django.utils import timezone

def generate_ticket_code(length=10):
    """Generate a unique ticket code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_qr_code(data):
    """Generate QR code image from data."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECTION_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io)
    img_io.seek(0)
    
    return img_io

def generate_pdf_ticket(booking):
    """Generate PDF ticket for a booking."""
    buffer = io.BytesIO()
    
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    c.setFont('Helvetica-Bold', 24)
    c.drawCentredString(width/2, height-1*inch, "District Events")
    
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width/2, height-1.5*inch, "E-Ticket")

    c.setFont('Helvetica-Bold', 14)
    c.drawString(1*inch, height-2.5*inch, "Event:")
    c.setFont('Helvetica', 14)
    c.drawString(2.5*inch, height-2.5*inch, booking.event.title)
    
    c.setFont('Helvetica-Bold', 14)
    c.drawString(1*inch, height-3*inch, "Date:")
    c.setFont('Helvetica', 14)
    c.drawString(2.5*inch, height-3*inch, booking.event.start_date.strftime('%d %b %Y'))
    
    c.setFont('Helvetica-Bold', 14)
    c.drawString(1*inch, height-3.5*inch, "Time:")
    c.setFont('Helvetica', 14)
    c.drawString(2.5*inch, height-3.5*inch, booking.event.start_time.strftime('%I:%M %p'))
    
    c.setFont('Helvetica-Bold', 14)
    c.drawString(1*inch, height-4*inch, "Venue:")
    c.setFont('Helvetica', 14)
    c.drawString(2.5*inch, height-4*inch, booking.event.venue.name)
    
    # Booking details
    c.setFont('Helvetica-Bold', 14)
    c.drawString(1*inch, height-5*inch, "Ticket Number:")
    c.setFont('Helvetica', 14)
    c.drawString(2.5*inch, height-5*inch, booking.ticket_code)
    
    c.setFont('Helvetica-Bold', 14)
    if booking.seat:
        c.drawString(1*inch, height-5.5*inch, "Seat:")
        c.setFont('Helvetica', 14)
        c.drawString(2.5*inch, height-5.5*inch, f"{booking.seat.row}{booking.seat.number}")
    elif booking.zone:
        c.drawString(1*inch, height-5.5*inch, "Zone:")
        c.setFont('Helvetica', 14)
        c.drawString(2.5*inch, height-5.5*inch, f"{booking.zone.name} (Qty: {booking.quantity})")

    c.setFont('Helvetica-Bold', 14)
    c.drawString(1*inch, height-6*inch, "Name:")
    c.setFont('Helvetica', 14)
    c.drawString(2.5*inch, height-6*inch, f"{booking.user.first_name} {booking.user.last_name}")
 
    qr_data = {
        'ticket_code': booking.ticket_code,
        'event': booking.event.title,
        'date': booking.event.start_date.strftime('%d %b %Y'),
        'name': f"{booking.user.first_name} {booking.user.last_name}",
    }
    
    if booking.seat:
        qr_data['seat'] = f"{booking.seat.row}{booking.seat.number}"
    elif booking.zone:
        qr_data['zone'] = booking.zone.name
        qr_data['quantity'] = booking.quantity
    
    qr_img = generate_qr_code(str(qr_data))

    img = Image(qr_img, width=2*inch, height=2*inch)
    img.drawOn(c, width-3*inch, height-7*inch)
    
    c.setFont('Helvetica-Oblique', 10)
    c.drawCentredString(width/2, 1*inch, "This is an electronically generated ticket.")
    c.drawCentredString(width/2, 0.8*inch, "Please present this ticket at the venue entrance.")
    c.drawCentredString(width/2, 0.6*inch, f"Issued on: {timezone.now().strftime('%d %b %Y, %I:%M %p')}")
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer.getvalue()

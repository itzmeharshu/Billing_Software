# bill_generator.py
from reportlab.pdfgen import canvas
import os

def generate_pdf(bill_id, party, truck, item, qty, payment, date):
    if not os.path.exists("bills"):
        os.makedirs("bills")

    filename = f"bills/bill_{bill_id}.pdf"
    pdf = canvas.Canvas(filename)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(180, 800, "Sri Elumalaiyan Bule Metals")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, f"Bill ID: {bill_id}")
    pdf.drawString(50, 740, f"Date: {date}")
    pdf.drawString(50, 720, f"Party: {party}")
    pdf.drawString(50, 700, f"Truck No: {truck}")
    pdf.drawString(50, 680, f"Item: {item}")
    pdf.drawString(50, 660, f"Quantity: {qty} KG")
    pdf.drawString(50, 640, f"Payment Mode: {payment}")
    pdf.drawString(180, 600, "Thank you for your business!")
    pdf.save()

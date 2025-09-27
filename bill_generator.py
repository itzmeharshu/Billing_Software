import re
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A6
from datetime import datetime

def generate_pdf(bill_id, data):
    """
    Generates a PDF bill for Sri Elumalaiyan Blue Metals using the detailed thermal receipt format.
    """
    
    # Extract data with safe access
    ref_no = data.get('ref_no', '')
    party = data.get('party', '')
    loading = data.get('loading', '')
    unloading = data.get('unloading', '')
    truck = data.get('truck', '')
    item = data.get('item', '')
    hsn = data.get('hsn', '')
    empty_qty = data.get('empty_qty', 0.0)
    full_qty = data.get('full_qty', 0.0)
    net_qty = data.get('net_qty', 0.0)
    payment = data.get('payment', '')
    date_time_str = data.get('date_time', datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper())

    # --- Sanitize ref_no for file name safety ---
    safe_ref_no = re.sub(r'[\\/:*?"<>|]', '-', ref_no)
    file_name = f"Bill_SEBM_{bill_id}_{safe_ref_no}.pdf"
    
    c = canvas.Canvas(file_name, pagesize=A6)
    
    # Define constants
    outer_margin = 0.2 * inch 
    INNER_PADDING = 0.10 * inch 
    
    x_left_content = outer_margin + INNER_PADDING
    X_RIGHT_CONTENT_ANCHOR = A6[0] - outer_margin - INNER_PADDING 
    
    y_start_content = A6[1] - outer_margin - 0.2 * inch 
    line_spacing = 0.16 * inch 
    
    # Helper for drawing the thin dotted separator line
    def draw_separator(y):
        c.setLineWidth(0.5)
        c.setDash(3, 3)     
        c.line(outer_margin, y, A6[0] - outer_margin, y)
        c.setDash([])       
        
    # --- Outer Border (Dotted) ---
    c.setLineWidth(0.5) 
    c.setDash(3, 3) 
    c.rect(outer_margin, outer_margin, A6[0] - 2*outer_margin, A6[1] - 2*outer_margin)
    c.setDash([]) 
    

    # --- Header ---
    y = y_start_content
    # SEBM
    c.setFont("Courier-Bold", 12) 
    c.drawCentredString(A6[0] / 2, y, "SEBM")
    y -= line_spacing * 1.5
    # Sri Elumalaiyan Blue Metals
    c.setFont("Courier-Bold", 14)
    c.drawCentredString(A6[0] / 2, y, "Sri Elumalaiyan Blue Metals")
    y -= line_spacing * 1.2
    # GSTIN/UIN #:
    c.setFont("Courier-Bold", 9) 
    c.drawCentredString(A6[0] / 2, y, "GSTIN/UIN #:")
    y -= line_spacing * 0.8
    
    # --- Date and Time (Centered & BOLD) ---
    y -= line_spacing * 1.0 
    c.setFont("Courier-Bold", 9) 
    date_part_split = date_time_str.split(" TIME: ")
    date_part = date_part_split[0]
    time_part = date_part_split[1] if len(date_part_split) > 1 else ""
    date_time_centered_str = f"Date: {date_part} Time: {time_part}"
    c.drawCentredString(A6[0] / 2, y, date_time_centered_str) 
    
    # --- DC/Ref # (Centered & BOLD) ---
    y -= line_spacing * 1.5
    c.setFont("Courier-Bold", 10) 
    dc_ref_centered_str = f"DC/Ref #: {ref_no}"
    c.drawCentredString(A6[0] / 2, y, dc_ref_centered_str)
    
    y -= line_spacing * 0.5 
    
    # --- Separator below DC/Ref # ---
    draw_separator(y) 
    
    # --- Trip Details Header ---
    y -= line_spacing * 1.0
    c.setFont("Courier-Bold", 10) 
    c.drawCentredString(A6[0] / 2, y, "OUTGOING TRIP")
    y -= line_spacing * 0.5 

    # Field list
    fields = [
        ("Party :", party),
        ("Loading :", loading),
        ("UnLoading:", unloading),
        ("Transport:", party), 
        ("Truck #:", truck),
        ("Item :", item),
        ("HSN/SAC:", hsn),
    ]
    
    # Draw field list (Labels left-aligned, Values RIGHT-ALIGNED & BOLD)
    c.setFont("Courier-Bold", 10)
    for label, value in fields:
        y -= line_spacing * 1.2
        c.drawString(x_left_content, y, label) 
        c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, str(value)) 

    # --- Quantity Section (BOLD) ---
    y -= line_spacing * 1.0
    
    qty_fields = [
        ("Empty Qty:", f"{empty_qty:.3f} KG"),
        ("Full Qty :", f"{full_qty:.3f} KG"),
        ("Net Qty :", f"{net_qty:.3f} KG"),
    ]

    for label, value in qty_fields:
        y -= line_spacing * 1.2
        c.drawString(x_left_content, y, label)
        c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, value) 

    # --- Signature and Payment (BOLD) ---
    y -= line_spacing * 2.0 

    c.drawString(x_left_content, y, "Payment Mode:")
    c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, payment) 
    
    # --- Footer (Thanking Part) ---
    y -= line_spacing * 1.5 
    
    y -= line_spacing * 1.0
    c.setFont("Courier-Bold", 8) 
    c.drawCentredString(A6[0] / 2, y, "Thank you for your business.")
    y -= line_spacing * 1.0
    c.drawCentredString(A6[0] / 2, y, "Please visit Sri Elumalaiyan Blue Metals.")
    y -= line_spacing * 1.0
    c.drawCentredString(A6[0] / 2, y, "Call to know more.")
    
    # Save the PDF
    c.showPage()
    c.save()

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A6
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import time

# --- 1. BILL GENERATOR LOGIC (Mimicking bill_generator.py) ---

# Register Courier font for a receipt-like appearance
try:
    pdfmetrics.registerFont(TTFont('Mono', 'Courier.ttf'))
except:
    # Fallback if Courier.ttf isn't found, ReportLab's built-in fonts will be used
    pass # Keep it silent to clean up the console output

def generate_pdf(bill_id, data):
    """Generates a PDF bill that mimics the thermal receipt in the image."""
    
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
    date_time = data.get('date_time', datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper())

    # --- FIX 1: Sanitize ref_no for file name safety ---
    # Replace invalid file system characters with an underscore
    safe_ref_no = ref_no.replace('/', '-').replace('\\', '-').replace(':', '-').replace('*', '-').replace('?', '-').replace('"', '-').replace('<', '-').replace('>', '-').replace('|', '-')
    file_name = f"Bill_{bill_id}_{safe_ref_no}.pdf"
    
    c = canvas.Canvas(file_name, pagesize=A6)
    
    # Define starting coordinates and font size
    x_margin = 0.5 * inch
    y_start = A6[1] - 0.5 * inch # Top of the page
    line_height = 0.25 * inch
    font_size = 10
    
    # Helper for drawing lines
    def draw_line(y, thickness=1):
        c.setLineWidth(thickness)
        c.line(0.2 * inch, y, A6[0] - 0.2 * inch, y)

    # --- Header ---
    y = y_start
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(A6[0] / 2, y, "SEBM")
    y -= line_height
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(A6[0] / 2, y, "Sri Elumalaiyan Blue Metals")
    y -= line_height * 0.8
    c.setFont("Helvetica", 8)
    c.drawCentredString(A6[0] / 2, y, "GSTIN/UIN #:")
    y -= line_height * 0.8
    
    # --- Date and DC/Ref # ---
    draw_line(y)
    y -= line_height * 0.8
    c.setFont("Helvetica", 9)
    c.drawString(x_margin, y, date_time)
    
    y -= line_height * 0.8
    c.setFont("Helvetica", 10)
    c.drawString(x_margin, y, f"DC/Ref #: {ref_no}")
    y -= line_height * 0.8
    draw_line(y)
    
    # --- Trip Details ---
    y -= line_height * 0.8
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(A6[0] / 2, y, "OUTGOING TRIP")
    y -= line_height * 0.8
    draw_line(y)
    y -= line_height * 0.2 # Small buffer

    fields = [
        ("Party :", party),
        ("Loading :", loading),
        ("UnLoading:", unloading),
        ("Transport:", party), 
        ("Truck #:", truck),
        ("Item :", item),
        ("HSN/SAC:", hsn),
    ]
    
    # Draw field list
    c.setFont("Helvetica", 10)
    SMALL_LINE = line_height * 0.7 # --- FIX 2: Reduced vertical spacing ---
    
    for label, value in fields:
        y -= SMALL_LINE
        c.drawString(x_margin, y, label)
        c.drawString(x_margin + 1.2 * inch, y, str(value)) 

    # --- Quantity Section ---
    y -= line_height * 0.5
    
    qty_fields = [
        ("Empty Qty:", f"{empty_qty:.3f} KG"),
        ("Full Qty :", f"{full_qty:.3f} KG"),
        ("Net Qty :", f"{net_qty:.3f} KG"),
    ]

    for label, value in qty_fields:
        y -= SMALL_LINE
        c.drawString(x_margin, y, label)
        c.drawString(x_margin + 1.2 * inch, y, value) 

    # --- Signature and Payment ---
    y -= line_height * 0.5
    
    # --- FIX 3: Adjusted circle position to clear the Net Qty value ---
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    # Draw the circle to the right side, mimicking the stamp location
    c.circle(A6[0] - 1.2 * inch, y - 0.2 * inch, 0.3 * inch) 
    
    y -= line_height * 1.5 # Space for the stamp

    c.drawString(x_margin, y, "Payment Mode:")
    c.drawString(x_margin + 1.2 * inch, y, payment)
    
    # --- Footer (Thanking Part) ---
    y -= line_height * 2.5
    draw_line(y)
    y -= line_height 
    c.setFont("Helvetica", 8)
    c.drawCentredString(A6[0] / 2, y, "Thank you for your business.")
    y -= line_height * 0.8
    c.drawCentredString(A6[0] / 2, y, "Please visit Sri Elumalaiyan Blue Metals.")
    y -= line_height * 0.8
    c.drawCentredString(A6[0] / 2, y, "Call to know more.")
    
    # Save the PDF
    c.showPage()
    c.save()

# --- 2. DATABASE LOGIC (In-memory placeholder) ---

bill_records = []
current_bill_id = 1000

def insert_bill(**data):
    global current_bill_id
    current_bill_id += 1
    
    record = {
        'id': current_bill_id,
        'timestamp': time.time(),
        **data
    }
    bill_records.append(record)
    return current_bill_id

# --- 3. MAIN APPLICATION LOGIC ---

def update_preview():
    # Gather all fields
    ref_no = entry_ref.get()
    party = entry_party.get()
    loading = entry_loading.get()
    unloading = entry_unloading.get()
    truck = entry_truck.get()
    item = entry_item.get()
    hsn = entry_hsn.get()
    empty_qty_str = entry_empty_qty.get()
    full_qty_str = entry_full_qty.get()
    payment = entry_payment.get()
    # Format date and time for display
    date_time_display = datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper().replace("AM", "AM").replace("PM", "PM")

    # Calculate Net Qty
    net_qty_str = "N/A"
    try:
        empty_qty = float(empty_qty_str)
        full_qty = float(full_qty_str)
        net_qty = full_qty - empty_qty
        net_qty_str = f"{net_qty:.3f}"
        empty_qty_str = f"{empty_qty:.3f}"
        full_qty_str = f"{full_qty:.3f}"
    except ValueError:
        pass

    preview_text.delete("1.0", tk.END)
    
    # Simulate the receipt format
    preview_text.insert(tk.END, f"            SEBM\n")
    preview_text.insert(tk.END, f"    Sri Elumalaiyan Blue Metals\n")
    preview_text.insert(tk.END, f"          GSTIN/UIN #:\n")
    preview_text.insert(tk.END, f"-----------------------------------\n")
    preview_text.insert(tk.END, f"{date_time_display}\n")
    preview_text.insert(tk.END, f"DC/Ref #: {ref_no}\n")
    preview_text.insert(tk.END, f"-----------------------------------\n")
    preview_text.insert(tk.END, f"          OUTGOING TRIP\n")
    preview_text.insert(tk.END, f"-----------------------------------\n")
    preview_text.insert(tk.END, f"Party : {party}\n")
    preview_text.insert(tk.END, f"Loading : {loading}\n")
    preview_text.insert(tk.END, f"UnLoading: {unloading}\n")
    preview_text.insert(tk.END, f"Transport: {party}\n") 
    preview_text.insert(tk.END, f"Truck #: {truck}\n")
    preview_text.insert(tk.END, f"Item : {item}\n")
    preview_text.insert(tk.END, f"HSN/SAC: {hsn}\n")
    preview_text.insert(tk.END, f"Empty Qty: {empty_qty_str} KG\n")
    preview_text.insert(tk.END, f"Full Qty : {full_qty_str} KG\n")
    preview_text.insert(tk.END, f"Net Qty : {net_qty_str} KG\n")
    preview_text.insert(tk.END, f"\n")
    preview_text.insert(tk.END, f"Payment Mode: {payment}\n")
    preview_text.insert(tk.END, f"\nThank you for your business!")
    

def generate_bill():
    # Gather all fields
    ref_no = entry_ref.get()
    party = entry_party.get()
    loading = entry_loading.get()
    unloading = entry_unloading.get()
    truck = entry_truck.get()
    item = entry_item.get()
    hsn = entry_hsn.get()
    empty_qty_str = entry_empty_qty.get()
    full_qty_str = entry_full_qty.get()
    payment = entry_payment.get()
    
    # Format date and time for PDF
    date_time = datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper().replace("AM", "AM").replace("PM", "PM")

    if not (ref_no and party and truck and item and hsn and empty_qty_str and full_qty_str and payment):
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        empty_qty = float(empty_qty_str)
        full_qty = float(full_qty_str)
        net_qty = full_qty - empty_qty
    except ValueError:
        messagebox.showerror("Error", "Quantities must be numbers")
        return

    # Compile data dictionary
    data = {
        'ref_no': ref_no,
        'party': party,
        'loading': loading,
        'unloading': unloading,
        'truck': truck,
        'item': item,
        'hsn': hsn,
        'empty_qty': empty_qty,
        'full_qty': full_qty,
        'net_qty': net_qty,
        'payment': payment,
        'date_time': date_time,
    }

    # Save to DB (In-memory list)
    bill_id = insert_bill(**data)

    # Generate PDF
    generate_pdf(bill_id, data)

    # Update Preview
    update_preview()

    messagebox.showinfo("Success", f"✅ Bill {bill_id} saved & PDF generated! Check your current directory for the file.")


# ---------------- GUI -----------------
root = tk.Tk()
root.title("Sri Elumalaiyan Blue Metals Billing")

# Left Frame (Form)
frame_left = tk.Frame(root, padx=20, pady=20)
frame_left.pack(side="left", fill="y")

# --- Form Fields ---

# Row 0
tk.Label(frame_left, text="DC/Ref #").grid(row=0, column=0, sticky="w")
entry_ref = tk.Entry(frame_left)
entry_ref.grid(row=0, column=1)

# Row 1
tk.Label(frame_left, text="Party Name (Transport)").grid(row=1, column=0, sticky="w")
entry_party = tk.Entry(frame_left)
entry_party.grid(row=1, column=1)

# Row 2
tk.Label(frame_left, text="Loading").grid(row=2, column=0, sticky="w")
entry_loading = tk.Entry(frame_left)
entry_loading.insert(0, "CRUSHER") # Pre-fill as per image
entry_loading.grid(row=2, column=1)

# Row 3
tk.Label(frame_left, text="UnLoading").grid(row=3, column=0, sticky="w")
entry_unloading = tk.Entry(frame_left)
entry_unloading.insert(0, "PARTY SITE") # Pre-fill as per image
entry_unloading.grid(row=3, column=1)

# Row 4
tk.Label(frame_left, text="Truck No (TN 12...)").grid(row=4, column=0, sticky="w")
entry_truck = tk.Entry(frame_left)
entry_truck.grid(row=4, column=1)

# Row 5
tk.Label(frame_left, text="Item").grid(row=5, column=0, sticky="w")
entry_item = tk.Entry(frame_left)
entry_item.insert(0, "GRAVEL") # Pre-fill as per image
entry_item.grid(row=5, column=1)

# Row 6
tk.Label(frame_left, text="HSN/SAC").grid(row=6, column=0, sticky="w")
entry_hsn = tk.Entry(frame_left)
entry_hsn.insert(0, "25171010") # Pre-fill as per image
entry_hsn.grid(row=6, column=1)

# Row 7
tk.Label(frame_left, text="Empty Qty (KG)").grid(row=7, column=0, sticky="w")
entry_empty_qty = tk.Entry(frame_left)
entry_empty_qty.grid(row=7, column=1)

# Row 8
tk.Label(frame_left, text="Full Qty (KG)").grid(row=8, column=0, sticky="w")
entry_full_qty = tk.Entry(frame_left)
entry_full_qty.grid(row=8, column=1)

# Row 9 (Empty for spacing)
tk.Label(frame_left, text="").grid(row=9, column=0, sticky="w")

# Row 10
tk.Label(frame_left, text="Payment Mode").grid(row=10, column=0, sticky="w")
entry_payment = tk.Entry(frame_left)
entry_payment.insert(0, "CASH") # Pre-fill as per image
entry_payment.grid(row=10, column=1)


tk.Button(frame_left, text="Preview", command=update_preview).grid(row=11, column=0, pady=10)
tk.Button(frame_left, text="Generate Bill", command=generate_bill).grid(row=11, column=1, pady=10)

# Right Frame (Preview)
frame_right = tk.Frame(root, padx=20, pady=20)
frame_right.pack(side="right", expand=True, fill="both")

tk.Label(frame_right, text="Live Bill Preview", font=("Arial", 14, "bold")).pack()
preview_text = tk.Text(frame_right, width=50, height=30, font=("Courier", 10))
preview_text.pack()

root.mainloop()
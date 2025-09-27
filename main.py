import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A6
from reportlab.pdfbase import pdfmetrics
import os
import time
import re # Import regex for safer file name sanitization

# --- 1. BILL GENERATOR LOGIC (PDF Generation) ---

def generate_pdf(bill_id, data):
    """
    Generates a PDF bill that mimics the thermal receipt in the image.
    Uses precise positioning and right alignment for numerical values.
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
    # date_time_str is pre-formatted as "DD-MM-YYYY Time: HH:MMAM/PM"
    date_time_str = data.get('date_time', datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper())

    # --- Sanitize ref_no for file name safety ---
    safe_ref_no = re.sub(r'[\\/:*?"<>|]', '-', ref_no)
    file_name = f"Bill_{bill_id}_{safe_ref_no}.pdf"
    
    c = canvas.Canvas(file_name, pagesize=A6)
    
    # Define constants
    outer_margin = 0.2 * inch # Margin from edge of the A6 page
    
    # NEW: Further reduced horizontal padding for content alignment (was 0.20 inch, now 0.15 inch)
    INNER_PADDING = 0.15 * inch
    
    # Left Content Anchor: Used for all labels (Party:, Empty Qty:)
    x_left_content = outer_margin + INNER_PADDING
    
    # Right Content Anchor: Used for right-justifying quantities (KG values) and all detail values (RKS, CRUSHER)
    X_RIGHT_CONTENT_ANCHOR = A6[0] - outer_margin - INNER_PADDING 
    
    y_start_content = A6[1] - outer_margin - 0.2 * inch # Top edge for text content
    line_spacing = 0.16 * inch # Base vertical spacing for compact look
    
    # Helper for drawing the thin separator lines
    def draw_separator(y):
        c.setLineWidth(0.5) # Thin line
        c.setDash(3, 3)     # Set to dotted line: 3 points on, 3 points off
        c.line(outer_margin, y, A6[0] - outer_margin, y)
        c.setDash([])       # FIX: Reset to solid line by passing an empty list
        
    # --- Outer Border (Dotted) ---
    c.setLineWidth(0.5) 
    c.setDash(3, 3) # Set the outer border to dotted
    c.rect(outer_margin, outer_margin, A6[0] - 2*outer_margin, A6[1] - 2*outer_margin)
    c.setDash([]) # Reset back to solid for internal content
    

    # --- Header ---
    y = y_start_content
    c.setFont("Courier", 12) 
    c.drawCentredString(A6[0] / 2, y, "SEBM")
    y -= line_spacing * 1.5
    c.setFont("Courier", 14)
    c.drawCentredString(A6[0] / 2, y, "Sri Elumalaiyan Blue Metals")
    y -= line_spacing * 1.2
    c.setFont("Courier", 9)
    c.drawCentredString(A6[0] / 2, y, "GSTIN/UIN #:")
    y -= line_spacing * 0.8
    
    # --- Date and Time (Centered) ---
    y -= line_spacing * 1.0 
    c.setFont("Courier", 9)
    
    # Prepare the date/time string for centering
    date_part_split = date_time_str.split(" TIME: ")
    date_part = date_part_split[0]
    time_part = date_part_split[1] if len(date_part_split) > 1 else ""
    
    # Centered Date and Time string
    date_time_centered_str = f"Date: {date_part} Time: {time_part}"
    c.drawCentredString(A6[0] / 2, y, date_time_centered_str) 
    
    # --- DC/Ref # (Centered) ---
    y -= line_spacing * 1.5
    c.setFont("Courier", 10)
    
    # Centered DC/Ref # string
    dc_ref_centered_str = f"DC/Ref #: {ref_no}"
    c.drawCentredString(A6[0] / 2, y, dc_ref_centered_str)
    
    y -= line_spacing * 0.5 
    
    # --- Line 2 (Below DC/Ref #) ---
    # KEEP: Separator below DC/Ref #, now DOTTED
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
        ("Transport:", party), # Assumes transport is the same as party
        ("Truck #:", truck),
        ("Item :", item),
        ("HSN/SAC:", hsn),
    ]
    
    # Draw field list (Labels left-aligned, Values RIGHT-ALIGNED at X_RIGHT_CONTENT_ANCHOR)
    c.setFont("Courier", 10)
    
    for label, value in fields:
        y -= line_spacing * 1.2
        c.drawString(x_left_content, y, label) 
        # Right-aligning all detail values to the common anchor
        c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, str(value)) 

    # --- Quantity Section ---
    y -= line_spacing * 1.0
    
    qty_fields = [
        ("Empty Qty:", f"{empty_qty:.3f} KG"),
        ("Full Qty :", f"{full_qty:.3f} KG"),
        ("Net Qty :", f"{net_qty:.3f} KG"),
    ]

    # Draw quantity list (Labels left-aligned, Values RIGHT-ALIGNED)
    for label, value in qty_fields:
        y -= line_spacing * 1.2
        c.drawString(x_left_content, y, label)
        c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, value) 

    # --- Signature and Payment ---
    y -= line_spacing * 2.0 # Space for the physical stamp/signature

    c.drawString(x_left_content, y, "Payment Mode:")
    # Value is RIGHT-ALIGNED to match the alignment of quantities in the image
    c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, payment) 
    
    # --- Footer (Thanking Part) ---
    y -= line_spacing * 1.5 
    
    # Horizontal line just above the Thank You message
    
    y -= line_spacing * 1.0
    c.setFont("Courier", 8)
    c.drawCentredString(A6[0] / 2, y, "Thank you for your business.")
    y -= line_spacing * 1.0
    c.drawCentredString(A6[0] / 2, y, "Please visit Sri Elumalaiyan Blue Metals.")
    y -= line_spacing * 1.0
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

# Function to format lines for the fixed-width preview
# REDUCED label_width from 10 to 9 to reduce gap
def format_preview_line(label, value, label_width=9):
    """Pads the label to a fixed width for clean column alignment in the preview."""
    padded_label = f"{label: <{label_width}}"
    return f"{padded_label}{value}\n"

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
    
    # Format date and time for PDF (includes " Time: ")
    date_time_for_pdf = datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper().replace("AM", "AM").replace("PM", "PM")
    
    # Calculate Net Qty
    net_qty_str = "N/A"
    empty_qty_f = 0.0
    full_qty_f = 0.0
    try:
        empty_qty_f = float(empty_qty_str)
        full_qty_f = float(full_qty_str)
        net_qty = full_qty_f - empty_qty_f
        net_qty_str = f"{net_qty:.3f}"
        empty_qty_str = f"{empty_qty_f:.3f}"
        full_qty_str = f"{full_qty_f:.3f}"
    except ValueError:
        pass

    # Split date and time for cleaner preview formatting
    date_part = ""
    time_part = ""
    if " TIME: " in date_time_for_pdf:
        parts = date_time_for_pdf.split(" TIME: ")
        date_part = parts[0]
        time_part = parts[1] if len(parts) > 1 else ""
    else:
        date_part = date_time_for_pdf

    # Helper for centering text in the fixed-width Text widget (40 chars wide)
    def center_preview_line(text, total_width=40):
        padding = (total_width - len(text)) // 2
        return f"{' ' * padding}{text}{' ' * (total_width - len(text) - padding)}\n"
        
    preview_text.delete("1.0", tk.END)
    
    # --- Simulate the receipt format (Fixed-width for alignment) ---
    preview_text.insert(tk.END, f"            SEBM\n")
    preview_text.insert(tk.END, f"    Sri Elumalaiyan Blue Metals\n")
    preview_text.insert(tk.END, f"          GSTIN/UIN #:\n")
    
    # Dotted Outer Border (Simulated for top)
    preview_text.insert(tk.END, f". . . . . . . . . . . . . . . . . . .\n")
    
    # Centered Date and Time
    date_time_centered_str = f"Date: {date_part} Time: {time_part}"
    preview_text.insert(tk.END, center_preview_line(date_time_centered_str))
    
    # Centered DC/Ref #
    dc_ref_centered_str = f"DC/Ref #: {ref_no}"
    preview_text.insert(tk.END, center_preview_line(dc_ref_centered_str))
    
    # Dotted Separator line
    preview_text.insert(tk.END, f"- - - - - - - - - - - - - - - - - -\n") 
    
    preview_text.insert(tk.END, f"          OUTGOING TRIP\n")
    
    # Use the formatting helper for consistent left-column alignment
    # Adjusted from 17 to 18 to align cleanly with reduced label width (9)
    MAX_TEXT_WIDTH = 18 
    
    def format_detail_line(label, value):
        padded_value = f"{value: >{MAX_TEXT_WIDTH}}"
        return format_preview_line(label, padded_value)
        
    preview_text.insert(tk.END, format_detail_line("Party :", party))
    preview_text.insert(tk.END, format_detail_line("Loading :", loading))
    preview_text.insert(tk.END, format_detail_line("UnLoading:", unloading))
    preview_text.insert(tk.END, format_detail_line("Transport:", party)) 
    preview_text.insert(tk.END, format_detail_line("Truck #:", truck))
    preview_text.insert(tk.END, format_detail_line("Item :", item))
    preview_text.insert(tk.END, format_detail_line("HSN/SAC:", hsn))
    
    # Quantity lines - must look right-aligned (using spaces to push the value right)
    
    # Max width for KG values to align them properly
    MAX_KG_WIDTH = 12 
    
    # Helper for right-aligning the KG values in the preview
    def format_qty_line(label, qty_str):
        # Adjusted padding for the value to align with MAX_TEXT_WIDTH + " KG"
        padded_qty = f"{qty_str: >{MAX_KG_WIDTH}} KG" 
        return format_preview_line(label, padded_qty)
    
    preview_text.insert(tk.END, format_qty_line("Empty Qty:", empty_qty_str))
    preview_text.insert(tk.END, format_qty_line("Full Qty :", full_qty_str))
    preview_text.insert(tk.END, format_qty_line("Net Qty :", net_qty_str))
    preview_text.insert(tk.END, f"\n")
    
    # Payment mode value is also right-aligned in the preview
    # MAX_TEXT_WIDTH + 3 (for " KG") = 21 chars
    padded_payment = f"{payment: >{MAX_TEXT_WIDTH + 3}}"
    
    preview_text.insert(tk.END, format_preview_line("Payment Mode:", padded_payment))
    preview_text.insert(tk.END, f"\nThank you for your business!")

    # Dotted Outer Border (Simulated for bottom)
    preview_text.insert(tk.END, f". . . . . . . . . . . . . . . . . . .\n")
    

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
tk.Label(frame_left, text="DC/Ref #").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_ref = tk.Entry(frame_left)
entry_ref.grid(row=0, column=1, padx=5, pady=5)

# Row 1
tk.Label(frame_left, text="Party Name (Transport)").grid(row=1, column=0, sticky="w", padx=5, pady=5)
entry_party = tk.Entry(frame_left)
entry_party.grid(row=1, column=1, padx=5, pady=5)
entry_party.insert(0, "RKS") # Example data

# Row 2
tk.Label(frame_left, text="Loading").grid(row=2, column=0, sticky="w", padx=5, pady=5)
entry_loading = tk.Entry(frame_left)
entry_loading.insert(0, "CRUSHER") # Pre-fill as per image
entry_loading.grid(row=2, column=1, padx=5, pady=5)

# Row 3
tk.Label(frame_left, text="UnLoading").grid(row=3, column=0, sticky="w", padx=5, pady=5)
entry_unloading = tk.Entry(frame_left)
entry_unloading.insert(0, "PARTY SITE") # Pre-fill as per image
entry_unloading.grid(row=3, column=1, padx=5, pady=5)

# Row 4
tk.Label(frame_left, text="Truck No (TN 12...)").grid(row=4, column=0, sticky="w", padx=5, pady=5)
entry_truck = tk.Entry(frame_left)
entry_truck.insert(0, "TN 12 AW 4728") # Example data
entry_truck.grid(row=4, column=1, padx=5, pady=5)

# Row 5
tk.Label(frame_left, text="Item").grid(row=5, column=0, sticky="w", padx=5, pady=5)
entry_item = tk.Entry(frame_left)
entry_item.insert(0, "GRAVEL") # Pre-fill as per image
entry_item.grid(row=5, column=1, padx=5, pady=5)

# Row 6
tk.Label(frame_left, text="HSN/SAC").grid(row=6, column=0, sticky="w", padx=5, pady=5)
entry_hsn = tk.Entry(frame_left)
entry_hsn.insert(0, "25171010") # Pre-fill as per image
entry_hsn.grid(row=6, column=1, padx=5, pady=5)

# Row 7
tk.Label(frame_left, text="Empty Qty (KG)").grid(row=7, column=0, sticky="w", padx=5, pady=5)
entry_empty_qty = tk.Entry(frame_left)
entry_empty_qty.insert(0, "15.560") # Example data
entry_empty_qty.grid(row=7, column=1, padx=5, pady=5)

# Row 8
tk.Label(frame_left, text="Full Qty (KG)").grid(row=8, column=0, sticky="w", padx=5, pady=5)
entry_full_qty = tk.Entry(frame_left)
entry_full_qty.insert(0, "69.580") # Example data
entry_full_qty.grid(row=8, column=1, padx=5, pady=5)

# Row 9 (Empty for spacing)
tk.Label(frame_left, text="").grid(row=9, column=0, sticky="w")

# Row 10
tk.Label(frame_left, text="Payment Mode").grid(row=10, column=0, sticky="w", padx=5, pady=5)
entry_payment = tk.Entry(frame_left)
entry_payment.insert(0, "CASH") # Pre-fill as per image
entry_payment.grid(row=10, column=1, padx=5, pady=5)


tk.Button(frame_left, text="Preview", command=update_preview, bg="#E6F0FF", fg="#0056D6").grid(row=11, column=0, pady=10, sticky="ew", padx=5)
tk.Button(frame_left, text="Generate Bill", command=generate_bill, bg="#0056D6", fg="white").grid(row=11, column=1, pady=10, sticky="ew", padx=5)

# Right Frame (Preview)
frame_right = tk.Frame(root, padx=20, pady=20, bg="#f5f5f5")
frame_right.pack(side="right", expand=True, fill="both")

tk.Label(frame_right, text="Live Bill Preview", font=("Courier", 14, "bold"), bg="#f5f5f5").pack()
# Set width to 40 characters for better fixed-width simulation
preview_text = tk.Text(frame_right, width=40, height=30, font=("Courier", 10), relief=tk.SUNKEN, borderwidth=3, bg="white")
preview_text.pack(fill="both", expand=True)

# Run initial preview
update_preview()

root.mainloop()

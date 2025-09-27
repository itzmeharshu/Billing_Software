import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A6
import os
import time
import re

# --- 1. SLIP GENERATOR LOGIC (PDF Generation - THERMAL STYLE) ---

def generate_pdf(slip_id, data):
    """
    Generates a PDF Weighment Slip for JCK Bluemetals using the advanced 
    thermal receipt style (bold, centered header, dotted border, right-aligned values).
    """
    
    # Extract data with safe access
    dc_ref = data.get('dc_ref', '')
    bill_no = data.get('bill_no', '')
    party_name = data.get('party_name', '')
    vehicle_no = data.get('vehicle_no', '')
    product = data.get('product', '')
    location = data.get('location', '')
    unloading_place = data.get('unloading_place', '')
    load_weight = data.get('load_weight', 0.0)
    empty_weight = data.get('empty_weight', 0.0)
    net_weight = data.get('net_weight', 0.0)
    quantity = data.get('quantity', 0.0)
    driver_beta = data.get('driver_beta', '')
    
    # Date/Time format matching the Sri Elumalaiyan standard
    date_time_str = datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper()
    data['date_time'] = date_time_str # Update data for internal consistency

    # --- Sanitize ref_no for file name safety ---
    safe_dc_ref = re.sub(r'[\\/:*?"<>|]', '-', dc_ref)
    file_name = f"Slip_JCK_{slip_id}_{safe_dc_ref}.pdf"
    
    c = canvas.Canvas(file_name, pagesize=A6)
    
    # --- CONSTANTS for THERMAL STYLE ---
    outer_margin = 0.2 * inch 
    
    # REDUCED INNER PADDING and adjusted anchors for less gap between L/R content
    INNER_PADDING = 0.05 * inch 
    x_left_content = outer_margin + INNER_PADDING
    
    # Alignment point for the colon (:) character (fixed horizontal position)
    X_COLON_ALIGN = x_left_content + 1.5 * inch # Adjusted to 1.5 inch
    
    # Right Content Anchor: Used for right-justifying all detail values
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
    
    # --- Header (BOLD and Centered) ---
    y = y_start_content
    c.setFont("Courier-Bold", 12) 
    c.drawCentredString(A6[0] / 2, y, "JCK Bluemetals")
    y -= line_spacing * 1.5
    c.setFont("Courier-Bold", 14)
    c.drawCentredString(A6[0] / 2, y, "Weighment Slip")
    y -= line_spacing * 1.2
    c.setFont("Courier-Bold", 9) 
    c.drawCentredString(A6[0] / 2, y, "SLIP ID: " + str(slip_id))
    y -= line_spacing * 0.8
    
    # --- Date and Time (Centered & BOLD) ---
    y -= line_spacing * 1.0 
    c.setFont("Courier-Bold", 9) 
    
    date_part_split = date_time_str.split(" TIME: ")
    date_part = date_part_split[0]
    time_part = date_part_split[1] if len(date_part_split) > 1 else ""
    date_time_centered_str = f"Date: {date_part} Time: {time_part}"
    c.drawCentredString(A6[0] / 2, y, date_time_centered_str) 
    
    # --- DC # and Bill # (LEFT-ALIGNED, SEPARATE LINES) ---
    y -= line_spacing * 1.5
    c.setFont("Courier-Bold", 10) 
    
    # DC #
    c.drawString(x_left_content, y, f"DC # : {dc_ref}")
    y -= line_spacing * 1.2
    
    # Bill #
    c.drawString(x_left_content, y, f"Bill # : {bill_no}")
    
    y -= line_spacing * 0.5 
    
    # --- Separator Line (Dotted) ---
    draw_separator(y) 
    
    # --- Itemized Details ---
    y -= line_spacing * 1.5 

    # List of fields (Labels left-aligned, Values RIGHT-ALIGNED)
    fields = [
        ("Party Name", party_name),
        ("Vehicle No", vehicle_no),
        ("Product", product),
        ("Location", location),
        ("UnLoading Place", unloading_place),
    ]
    
    c.setFont("Courier-Bold", 10)
    
    # Draw non-weight fields
    for label, value in fields:
        y -= line_spacing * 1.2
        c.drawString(x_left_content, y, label) 
        c.drawString(X_COLON_ALIGN, y, ":") # Align the colon
        c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, str(value)) 

    # --- Weight Section ---
    y -= line_spacing * 1.0
    
    weight_fields = [
        ("Load Weight", f"{load_weight:.0f} KG"),
        ("Empty Weight", f"{empty_weight:.0f} KG"),
        ("Net Weight", f"{net_weight:.0f} KG"),
    ]

    # Draw weight fields
    for label, value in weight_fields:
        y -= line_spacing * 1.2
        c.drawString(x_left_content, y, label)
        c.drawString(X_COLON_ALIGN, y, ":") # Align the colon
        c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, value) 
        
    # --- Quantity and Driver Beta ---
    y -= line_spacing * 1.0

    c.drawString(x_left_content, y, "Quantity")
    c.drawString(X_COLON_ALIGN, y, ":") # Align the colon
    c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, f"{quantity:.2f} MT") 
    y -= line_spacing * 1.2
    
    c.drawString(x_left_content, y, "Driver Beta")
    c.drawString(X_COLON_ALIGN, y, ":") # Align the colon
    c.drawRightString(X_RIGHT_CONTENT_ANCHOR, y, driver_beta) 

    # --- Footer (Thanking Part - BOLD and Centered) ---
    y -= line_spacing * 2.5 
    
    c.setFont("Courier-Bold", 8) 
    c.drawCentredString(A6[0] / 2, y, "Thank you for your business.")
    y -= line_spacing * 1.0
    c.drawCentredString(A6[0] / 2, y, "Please visit JCK Bluemetals.")
    y -= line_spacing * 1.0
    c.drawCentredString(A6[0] / 2, y, "Call to know more.")
    
    # Save the PDF
    c.showPage()
    c.save()

# --- 2. DATABASE LOGIC (In-memory placeholder) ---

slip_records = []
current_slip_id = 2000

def insert_slip(**data):
    global current_slip_id
    current_slip_id += 1
    
    record = {
        'id': current_slip_id,
        'timestamp': time.time(),
        **data
    }
    slip_records.append(record)
    return current_slip_id

# --- 3. MAIN APPLICATION LOGIC ---

# Function to format lines for the fixed-width preview
def format_preview_line(label, value, label_width=16): 
    """Pads the label to a fixed width for clean column alignment in the preview."""
    padded_label = f"{label: <{label_width}}"
    return f"{padded_label}{value}\n"

def update_preview(preview_text_widget, entry_vars):
    
    dc_ref, bill_no, party_name, vehicle_no, product, location, unloading_place, \
        load_weight_str, empty_weight_str, driver_beta = entry_vars

    # Calculate Net Weight and Quantity
    net_weight_str = "N/A"
    quantity_str = "N/A"
    try:
        load_weight = float(load_weight_str.get())
        empty_weight = float(empty_weight_str.get())
        net_weight = load_weight - empty_weight
        quantity = net_weight / 1000.0 # Convert KG to MT
        
        net_weight_str = f"{net_weight:.0f}"
        quantity_str = f"{quantity:.2f}"
    except ValueError:
        load_weight = 0.0
        empty_weight = 0.0

    # Date/Time format matching the Sri Elumalaiyan standard
    date_time_for_pdf = datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper().replace("AM", "AM").replace("PM", "PM")
    date_part_split = date_time_for_pdf.split(" TIME: ")
    date_part = date_part_split[0]
    time_part = date_part_split[1] if len(date_part_split) > 1 else ""

    
    preview_text_widget.delete("1.0", tk.END)
    
    # Helper for centering text in the fixed-width Text widget (40 chars wide)
    def center_preview_line(text, total_width=40):
        padding = (total_width - len(text)) // 2
        return f"{' ' * padding}{text}{' ' * (total_width - len(text) - padding)}\n"

    # Helper for column alignment (Label : Value) - REDUCED GAP
    COLON_OFFSET = 18 # Position of the colon
    VALUE_OFFSET = 2 # Position of value relative to colon
    def format_slip_line_preview(label, value):
        colon_space = COLON_OFFSET - len(label)
        value_space = VALUE_OFFSET
        
        # Ensures alignment: [Label] [spaces] : [spaces] [Value]
        return f"{label}{' ' * colon_space}:{' ' * value_space}{value}\n"
    
    # --- Simulate the receipt format ---
    preview_text_widget.insert(tk.END, center_preview_line("JCK Bluemetals", 40))
    preview_text_widget.insert(tk.END, center_preview_line("Weighment Slip", 40))
    preview_text_widget.insert(tk.END, center_preview_line("SLIP ID: 2000", 40)) 
    
    # Dotted Outer Border (Simulated for top)
    preview_text_widget.insert(tk.END, f". . . . . . . . . . . . . . . . . . .\n")
    
    # Centered Date and Time
    date_time_centered_str = f"Date: {date_part} Time: {time_part}"
    preview_text_widget.insert(tk.END, center_preview_line(date_time_centered_str))
    
    # LEFT-ALIGNED DC/Bill #
    preview_text_widget.insert(tk.END, f"DC # : {dc_ref.get()}\n")
    preview_text_widget.insert(tk.END, f"Bill # : {bill_no.get()}\n")
    
    # Dotted Separator line
    preview_text_widget.insert(tk.END, f"- - - - - - - - - - - - - - - - - -\n") 
    
    preview_text_widget.insert(tk.END, f"\n") # Spacing for separation
    
    # Itemized Details (Colon-Aligned)
    preview_text_widget.insert(tk.END, format_slip_line_preview("Party Name", party_name.get()))
    preview_text_widget.insert(tk.END, format_slip_line_preview("Vehicle No", vehicle_no.get()))
    preview_text_widget.insert(tk.END, format_slip_line_preview("Product", product.get()))
    preview_text_widget.insert(tk.END, format_slip_line_preview("Location", location.get()))
    preview_text_widget.insert(tk.END, format_slip_line_preview("UnLoading Place", unloading_place.get()))
    
    # Weights and Quantity
    preview_text_widget.insert(tk.END, format_slip_line_preview("Load Weight", f"{load_weight_str.get()} KG"))
    preview_text_widget.insert(tk.END, format_slip_line_preview("Empty Weight", f"{empty_weight_str.get()} KG"))
    preview_text_widget.insert(tk.END, format_slip_line_preview("Net Weight", f"{net_weight_str} KG"))
    preview_text_widget.insert(tk.END, format_slip_line_preview("Quantity", f"{quantity_str} MT"))
    
    # Driver Beta
    preview_text_widget.insert(tk.END, format_slip_line_preview("Driver Beta", driver_beta.get()))
    
    preview_text_widget.insert(tk.END, f"\n")
    preview_text_widget.insert(tk.END, center_preview_line("Thank you for your business."))
    preview_text_widget.insert(tk.END, center_preview_line("Please visit JCK Bluemetals."))
    preview_text_widget.insert(tk.END, center_preview_line("Call to know more."))

    # Dotted Outer Border (Simulated for bottom)
    preview_text_widget.insert(tk.END, f". . . . . . . . . . . . . . . . . . .\n")
    

def generate_slip(entry_vars, preview_text_widget):
    
    dc_ref_var, bill_no_var, party_name_var, vehicle_no_var, product_var, location_var, \
        unloading_place_var, load_weight_str_var, empty_weight_str_var, driver_beta_var = entry_vars

    dc_ref = dc_ref_var.get()
    bill_no = bill_no_var.get()
    party_name = party_name_var.get()
    vehicle_no = vehicle_no_var.get()
    product = product_var.get()
    location = location_var.get()
    unloading_place = unloading_place_var.get()
    load_weight_str = load_weight_str_var.get()
    empty_weight_str = empty_weight_str_var.get()
    driver_beta = driver_beta_var.get()
    
    # Date/Time format matching the Sri Elumalaiyan standard
    date_time = datetime.now().strftime("%d-%m-%Y Time: %I:%M%p").upper().replace("AM", "AM").replace("PM", "PM")

    required_fields = [dc_ref, bill_no, party_name, vehicle_no, product, location, unloading_place, load_weight_str, empty_weight_str]
    if not all(required_fields):
        messagebox.showerror("Error", "All primary fields are required!")
        return

    try:
        load_weight = float(load_weight_str)
        empty_weight = float(empty_weight_str)
        net_weight = load_weight - empty_weight
        quantity = net_weight / 1000.0
    except ValueError:
        messagebox.showerror("Error", "Weights must be numbers")
        return
        
    if net_weight <= 0:
        messagebox.showwarning("Warning", "Net Weight is zero or negative. Check Load and Empty Weights.")
        return

    # Compile data dictionary
    data = {
        'dc_ref': dc_ref,
        'bill_no': bill_no,
        'party_name': party_name,
        'vehicle_no': vehicle_no,
        'product': product,
        'location': location,
        'unloading_place': unloading_place,
        'load_weight': load_weight,
        'empty_weight': empty_weight,
        'net_weight': net_weight,
        'quantity': quantity,
        'driver_beta': driver_beta,
        'date_time': date_time,
    }

    # Save to DB (In-memory list)
    slip_id = insert_slip(**data)

    # Generate PDF
    generate_pdf(slip_id, data)

    # Update Preview
    update_preview(preview_text_widget, entry_vars)

    messagebox.showinfo("Success", f"✅ Slip {slip_id} saved & PDF generated! Check your current directory for the file.")


# ---------------- GUI -----------------
# CRUCIAL: Wrap GUI setup in __main__ to prevent accidental execution on import
if __name__ == "__main__":
    root = tk.Tk()
    root.title("JCK Bluemetals Weighment Slip")

    # Left Frame (Form)
    frame_left = tk.Frame(root, padx=20, pady=20)
    frame_left.pack(side="left", fill="y")

    # Entry variables storage
    entry_vars = []

    # Helper function to create labels and entries
    def create_form_row(container, row, label_text, default_value=""):
        tk.Label(container, text=label_text).grid(row=row, column=0, sticky="w", padx=5, pady=5)
        entry_var = tk.StringVar(root, value=default_value)
        entry = tk.Entry(container, textvariable=entry_var)
        entry.grid(row=row, column=1, padx=5, pady=5)
        entry_vars.append(entry_var)
        return entry_var, entry

    # --- Form Fields ---
    
    # Row 0
    dc_ref_var, _ = create_form_row(frame_left, 0, "DC #", "9000/01-01/B/S")

    # Row 1
    bill_no_var, _ = create_form_row(frame_left, 1, "Bill #", "5000/INV/26-27")

    # Row 2
    party_name_var, _ = create_form_row(frame_left, 2, "Party Name", "PLACEHOLDER TRADERS")
    
    # Row 3
    vehicle_no_var, _ = create_form_row(frame_left, 3, "Vehicle No", "TN99Z0000")
    
    # Row 4
    product_var, _ = create_form_row(frame_left, 4, "Product", "M-SAND NEW")

    # Row 5
    location_var, _ = create_form_row(frame_left, 5, "Location", "New Stockyard")
    
    # Row 6
    unloading_place_var, _ = create_form_row(frame_left, 6, "UnLoading Place", "TOWN SITE")

    # Row 7 (Load Weight)
    load_weight_str_var, load_weight_entry = create_form_row(frame_left, 7, "Load Weight (KG)", "35000")

    # Row 8 (Empty Weight)
    empty_weight_str_var, empty_weight_entry = create_form_row(frame_left, 8, "Empty Weight (KG)", "9000")
    
    # Row 9 (Driver Beta)
    driver_beta_var, _ = create_form_row(frame_left, 9, "Driver Beta", "N/A")


    # Right Frame (Preview)
    frame_right = tk.Frame(root, padx=20, pady=20, bg="#f5f5f5")
    frame_right.pack(side="right", expand=True, fill="both")

    tk.Label(frame_right, text="Live Weighment Slip Preview", font=("Courier", 12, "bold"), bg="#f5f5f5").pack()
    # Note: Font changed to bold Courier to match the thermal receipt style
    preview_text = tk.Text(frame_right, width=40, height=30, font=("Courier", 10, "bold"), relief=tk.SUNKEN, borderwidth=3, bg="white")
    preview_text.pack(fill="both", expand=True)
    
    # Bind update_preview to key releases on weight fields for live calculation
    def update_on_key(event=None):
        update_preview(preview_text, entry_vars)
        
    load_weight_entry.bind('<KeyRelease>', update_on_key)
    empty_weight_entry.bind('<KeyRelease>', update_on_key)

    # Buttons
    tk.Button(frame_left, text="Preview", command=lambda: update_preview(preview_text, entry_vars), bg="#E6F0FF", fg="#0056D6").grid(row=10, column=0, pady=10, sticky="ew", padx=5)
    tk.Button(frame_left, text="Generate Slip", command=lambda: generate_slip(entry_vars, preview_text), bg="#0056D6", fg="white").grid(row=10, column=1, pady=10, sticky="ew", padx=5)

    # Run initial preview
    update_preview(preview_text, entry_vars)

    root.mainloop()

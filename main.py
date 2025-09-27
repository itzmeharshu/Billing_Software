import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import database
import bill_generator

def update_preview():
    party = entry_party.get()
    truck = entry_truck.get()
    item = entry_item.get()
    qty = entry_qty.get()
    payment = entry_payment.get()
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    preview_text.delete("1.0", tk.END)
    preview_text.insert(tk.END, f"--- Sri Elumalaiyan Blue Metals ---\n")
    preview_text.insert(tk.END, f"Date: {date}\n")
    preview_text.insert(tk.END, f"Party: {party}\n")
    preview_text.insert(tk.END, f"Truck No: {truck}\n")
    preview_text.insert(tk.END, f"Item: {item}\n")
    preview_text.insert(tk.END, f"Quantity: {qty} KG\n")
    preview_text.insert(tk.END, f"Payment Mode: {payment}\n")
    preview_text.insert(tk.END, f"\nThank you for your business!")

def generate_bill():
    party = entry_party.get()
    truck = entry_truck.get()
    item = entry_item.get()
    qty = entry_qty.get()
    payment = entry_payment.get()
    date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    if not (party and truck and item and qty and payment):
        messagebox.showerror("Error", "All fields are required!")
        return

    try:
        qty = float(qty)
    except ValueError:
        messagebox.showerror("Error", "Quantity must be a number")
        return

    # Save to DB
    bill_id = database.insert_bill(party, truck, item, qty, payment, date)

    # Generate PDF
    bill_generator.generate_pdf(bill_id, party, truck, item, qty, payment, date)

    # Update Preview
    update_preview()

    messagebox.showinfo("Success", f"✅ Bill {bill_id} saved & PDF generated!")

# ---------------- GUI -----------------
root = tk.Tk()
root.title("Billing Software with Preview")

# Left Frame (Form)
frame_left = tk.Frame(root, padx=20, pady=20)
frame_left.pack(side="left", fill="y")

tk.Label(frame_left, text="Party Name").grid(row=0, column=0, sticky="w")
entry_party = tk.Entry(frame_left)
entry_party.grid(row=0, column=1)

tk.Label(frame_left, text="Truck No").grid(row=1, column=0, sticky="w")
entry_truck = tk.Entry(frame_left)
entry_truck.grid(row=1, column=1)

tk.Label(frame_left, text="Item").grid(row=2, column=0, sticky="w")
entry_item = tk.Entry(frame_left)
entry_item.grid(row=2, column=1)

tk.Label(frame_left, text="Quantity (KG)").grid(row=3, column=0, sticky="w")
entry_qty = tk.Entry(frame_left)
entry_qty.grid(row=3, column=1)

tk.Label(frame_left, text="Payment Mode").grid(row=4, column=0, sticky="w")
entry_payment = tk.Entry(frame_left)
entry_payment.grid(row=4, column=1)

tk.Button(frame_left, text="Preview", command=update_preview).grid(row=5, column=0, pady=10)
tk.Button(frame_left, text="Generate Bill", command=generate_bill).grid(row=5, column=1, pady=10)

# Right Frame (Preview)
frame_right = tk.Frame(root, padx=20, pady=20)
frame_right.pack(side="right", expand=True, fill="both")

tk.Label(frame_right, text="Live Bill Preview", font=("Arial", 14, "bold")).pack()
preview_text = tk.Text(frame_right, width=50, height=20, font=("Courier", 12))
preview_text.pack()

root.mainloop()

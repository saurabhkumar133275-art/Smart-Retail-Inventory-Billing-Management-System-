import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from reportlab.pdfgen import canvas
from datetime import datetime
import matplotlib.pyplot as plt
import urllib.parse
import webbrowser


# ================= DATABASE =================

conn = mysql.connector.connect(
    host="localhost",
    user="Saurabh",
    password="Saurabh@7352",
    database="retail_ai"
)

cursor = conn.cursor()

# ================= WHATSAPP =================

def send_whatsapp(customer, mobile, product, price, qty, total):

    mobile = "91" + mobile

    message = f"""
Thank you for shopping 🛍️

Customer : {customer}

Product : {product}
Price : ₹{price}
Quantity : {qty}

Total Bill : ₹{total}

Visit Again 🙏
"""

    encoded_message = urllib.parse.quote(message)

    url = f"https://wa.me/{mobile}?text={encoded_message}"

    webbrowser.open(url)


# ================= LOGIN =================

def login():

    cursor.execute(
        "select * from users where username=%s and password=%s",
        (username_entry.get(),password_entry.get())
    )

    if cursor.fetchone():

        login_win.destroy()
        main_screen()

    else:

        messagebox.showerror("Error","Invalid login")


def register():

    try:

        cursor.execute(
            "insert into users(username,password) values(%s,%s)",
            (username_entry.get(),password_entry.get())
        )

        conn.commit()

        messagebox.showinfo("Success","Account created")

    except:

        messagebox.showerror("Error","User exists")


# ================= MAIN SCREEN =================

def main_screen():

    root=tk.Tk()

    root.title("Smart Retail Management")
    root.geometry("500x680")
    root.configure(bg="#d1d5db")

# ---------- FUNCTIONS ----------

    def load_products():

        cursor.execute("select name from products")

        data=cursor.fetchall()

        product_combo['values']=[i[0] for i in data]

    def add_product():

        try:

            cursor.execute(
                "select quantity from products where id=%s",
                (id_entry.get(),)
            )

            result = cursor.fetchone()

        # agar same ID already hai → quantity increase
            if result:

                cursor.execute(
                    "update products set quantity = quantity + %s where id=%s",
                    (qty_entry.get(), id_entry.get())
                )

                messagebox.showinfo("Updated","Stock Increased")

        # agar new ID hai → new product add
            else:

                cursor.execute(
                    "insert into products(id,name,price,quantity) values(%s,%s,%s,%s)",
                    (
                        id_entry.get(),
                        name_entry.get(),
                        price_entry.get(),
                        qty_entry.get()
                    )
                )

                messagebox.showinfo("Done","Product Added")

            conn.commit()

            load_products()

        except Exception as e:

            messagebox.showerror("Error", str(e))

    def view_products():

        win=tk.Toplevel(root)

        win.title("Products")

        tree=ttk.Treeview(
            win,
            columns=("ID","Name","Price","Qty"),
            show="headings"
        )

        tree.heading("ID",text="ID")
        tree.heading("Name",text="Name")
        tree.heading("Price",text="Price")
        tree.heading("Qty",text="Quantity")

        tree.pack(fill="both",expand=True)

        cursor.execute("select * from products")

        for row in cursor.fetchall():

            tree.insert("", "end", values=row)


    def delete_product():

        cursor.execute(
            "delete from products where id=%s",
            (delete_id.get(),)
        )

        conn.commit()

        messagebox.showinfo("Deleted","Product deleted")

        load_products()


    def search_product():

        win=tk.Toplevel(root)

        tree=ttk.Treeview(
            win,
            columns=("ID","Name","Price","Qty"),
            show="headings"
        )

        tree.heading("ID",text="ID")
        tree.heading("Name",text="Name")
        tree.heading("Price",text="Price")
        tree.heading("Qty",text="Qty")

        tree.pack(fill="both",expand=True)

        cursor.execute(
            "select * from products where name like %s",
            ("%" + search_entry.get() + "%",)
        )

        for row in cursor.fetchall():

            tree.insert("", "end", values=row)


    def bill():

        name=product_combo.get()

        qty=int(bill_qty.get())

        cursor.execute(
            "select price,quantity from products where name=%s",
            (name,)
        )

        price,stock=cursor.fetchone()

        if qty>stock:

            messagebox.showerror("Error","Low stock")

            return

        total=price*qty

        cursor.execute(
            "update products set quantity=%s where name=%s",
            (stock-qty,name)
        )

        cursor.execute(
            "insert into sales(customer_name,mobile,product,quantity,total,date) values(%s,%s,%s,%s,%s,%s)",
            (
                customer_entry.get(),
                mobile_entry.get(),
                name,
                qty,
                total,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()

        create_invoice(name,price,qty,total)

        # WHATSAPP CALL CORRECT
        send_whatsapp(
            customer_entry.get(),
            mobile_entry.get(),
            name,
            price,
            qty,
            total
        )

        messagebox.showinfo("Bill","Invoice saved & WhatsApp opened")


    def create_invoice(product,price,qty,total):

        file=f"invoice_{datetime.now().strftime('%H%M%S')}.pdf"

        c=canvas.Canvas(file)

        c.setFont("Helvetica-Bold",16)

        c.drawString(180,800,"SMART RETAIL SHOP")

        c.setFont("Helvetica",12)

        c.drawString(50,740,f"Product : {product}")
        c.drawString(50,720,f"Price : {price}")
        c.drawString(50,700,f"Quantity : {qty}")
        c.drawString(50,680,f"Total : {total}")

        c.drawString(50,640,"Thank you for shopping!")

        c.save()


    def report():

        win = tk.Toplevel(root)
        win.title("Sales Report")

        tree = ttk.Treeview(
            win,
            columns=("ID","Customer","Mobile","Product","Qty","Total","Date"),
            show="headings"
        )

        for col in ("ID","Customer","Mobile","Product","Qty","Total","Date"):
            tree.heading(col, text=col)

        tree.pack(fill="both", expand=True)

        cursor.execute("SELECT * FROM sales")

        for row in cursor.fetchall():

            tree.insert("", "end", values=row)


    def dashboard():

        cursor.execute("select count(*) from products")

        p=cursor.fetchone()[0]

        cursor.execute("select sum(total) from sales")

        s=cursor.fetchone()[0]

        messagebox.showinfo(
            "Dashboard",
            f"Products = {p}\nRevenue = {s}"
        )


    def low_stock():

        cursor.execute(
            "select name,quantity from products where quantity<5"
        )

        messagebox.showinfo("Low Stock",cursor.fetchall())


    def graph():

        cursor.execute(
            "select product,sum(quantity) from sales group by product"
        )

        data=cursor.fetchall()

        x=[i[0] for i in data]

        y=[i[1] for i in data]

        plt.bar(x,y)

        plt.title("Sales Graph")

        plt.show()


# ---------- UI ----------

    tk.Label(
        root,
        text="Smart Retail Management",
        font=("Arial",18,"bold"),
        bg="#d1d5db"
    ).pack(pady=10)


# PRODUCT FRAME

    f1=tk.Frame(root,bg="#9ca3af",padx=20,pady=20)
    f1.pack(pady=10)

    tk.Label(f1,text="Product ID").grid(row=0,column=0)
    id_entry=tk.Entry(f1)
    id_entry.grid(row=0,column=1)

    tk.Label(f1,text="Product Name").grid(row=1,column=0)
    name_entry=tk.Entry(f1)
    name_entry.grid(row=1,column=1)

    tk.Label(f1,text="Price").grid(row=2,column=0)
    price_entry=tk.Entry(f1)
    price_entry.grid(row=2,column=1)

    tk.Label(f1,text="Quantity").grid(row=3,column=0)
    qty_entry=tk.Entry(f1)
    qty_entry.grid(row=3,column=1)

    tk.Button(f1,text="Add Product",bg="green",fg="white",command=add_product).grid(row=4,column=0)

    tk.Button(f1,text="View Products",bg="#2563eb",fg="white",command=view_products).grid(row=4,column=1)

    tk.Label(f1,text="Delete ID").grid(row=5,column=0)
    delete_id=tk.Entry(f1)
    delete_id.grid(row=5,column=1)

    tk.Button(f1,text="Delete Product",bg="red",fg="white",command=delete_product).grid(row=6,column=0)

    tk.Label(f1,text="Search").grid(row=7,column=0)
    search_entry=tk.Entry(f1)
    search_entry.grid(row=7,column=1)

    tk.Button(f1,text="Search Product",bg="#0ea5e9",fg="white",command=search_product).grid(row=8,column=0,columnspan=2)


# BILL FRAME

    f2=tk.Frame(root,bg="#9ca3af",padx=20,pady=20)
    f2.pack(pady=10)

    tk.Label(f2,text="Customer Name").grid(row=0,column=0)
    customer_entry=tk.Entry(f2)
    customer_entry.grid(row=0,column=1)

    tk.Label(f2,text="Mobile").grid(row=1,column=0)
    mobile_entry=tk.Entry(f2)
    mobile_entry.grid(row=1,column=1)

    tk.Label(f2,text="Product").grid(row=2,column=0)
    product_combo=ttk.Combobox(f2)
    product_combo.grid(row=2,column=1)

    tk.Label(f2,text="Quantity").grid(row=3,column=0)
    bill_qty=tk.Entry(f2)
    bill_qty.grid(row=3,column=1)

    tk.Button(f2,text="Generate Bill",bg="purple",fg="white",command=bill).grid(row=4,column=0,columnspan=2)


# REPORT BUTTONS

    tk.Button(root,text="Sales Report",bg="#374151",fg="white",command=report).pack(pady=3)

    tk.Button(root,text="Dashboard",bg="#10b981",fg="white",command=dashboard).pack(pady=3)

    tk.Button(root,text="Low Stock Alert",bg="#ea580c",fg="white",command=low_stock).pack(pady=3)

    tk.Button(root,text="Sales Graph",bg="#7c3aed",fg="white",command=graph).pack(pady=3)


    load_products()

    root.mainloop()


# LOGIN WINDOW

login_win=tk.Tk()

login_win.title("Login")
login_win.geometry("350x300")
login_win.configure(bg="#334155")

tk.Label(login_win,text="Retail System Login",font=("Arial",16,"bold"),fg="white",bg="#334155").pack(pady=15)

tk.Label(login_win,text="Username",bg="#334155",fg="white").pack()
username_entry=tk.Entry(login_win)
username_entry.pack(pady=5)

tk.Label(login_win,text="Password",bg="#334155",fg="white").pack()
password_entry=tk.Entry(login_win,show="*")
password_entry.pack(pady=5)

tk.Button(login_win,text="Login",bg="green",fg="white",width=15,command=login).pack(pady=5)

tk.Button(login_win,text="Register",bg="#2563eb",fg="white",width=15,command=register).pack()

login_win.mainloop()
try:
    import mysql.connector
except ModuleNotFoundError:
    print("ERROR: mysql-connector-python not installed.")
    print("Install it with: pip install mysql-connector-python")
    exit()
from mysql.connector import errorcode
from datetime import datetime
import sys

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "supermarket"}

def get_connection(create_db=False):
    cfg = DB_CONFIG.copy()
    if create_db:
        cfg_no_db = cfg.copy()
        cfg_no_db.pop("database", None)
        conn = mysql.connector.connect(**cfg_no_db)
        return conn
    return mysql.connector.connect(**cfg)

def create_database_and_tables():
    try:
        conn = get_connection(create_db=True)
        cur = conn.cursor()
        cur.execute("CREATE DATABASE IF NOT EXISTS supermarket")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Error creating database:", e)
        sys.exit(1)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock (
      product_id INT PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      quantity INT NOT NULL DEFAULT 0,
      selling_price DECIMAL(10,2) NOT NULL)""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customer (
      cu_id INT PRIMARY KEY,
      name VARCHAR(255) NOT NULL,
      mobile VARCHAR(15))""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
      bill_no INT PRIMARY KEY,
      cust_no INT,
      bill_date DATE NOT NULL,
      mode VARCHAR(10) NOT NULL,
      total_amount DECIMAL(12,2) NOT NULL,
      FOREIGN KEY (cust_no) REFERENCES customer(cu_id) ON DELETE SET NULL)""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bill_items (
      id INT AUTO_INCREMENT PRIMARY KEY,
      bill_no INT,
      product_id INT,
      qty INT NOT NULL,
      rate DECIMAL(10,2) NOT NULL,
      amount DECIMAL(12,2) NOT NULL,
      FOREIGN KEY (bill_no) REFERENCES bills(bill_no) ON DELETE CASCADE,
      FOREIGN KEY (product_id) REFERENCES stock(product_id) ON DELETE SET NULL)""")
    conn.commit()
    cur.close()
    conn.close()

def add_stock():
    try:
        conn = get_connection()
        cur = conn.cursor()
        product_id = int(input("Enter product ID (integer): ").strip())
        cur.execute("SELECT product_id FROM stock WHERE product_id=%s", (product_id,))
        if cur.fetchone():
            print("Product ID exists. Use update.")
            cur.close(); conn.close(); return
        name = input("Enter product name: ").strip()
        selling_price = float(input("Enter selling price: ").strip())
        quantity = int(input("Enter quantity: ").strip())
        cur.execute("INSERT INTO stock (product_id, name, quantity, selling_price) VALUES (%s,%s,%s,%s)",
                    (product_id, name, quantity, selling_price))
        conn.commit()
        print("Item added.")
    except ValueError:
        print("Invalid numeric input.")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def update_stock():
    try:
        conn = get_connection()
        cur = conn.cursor()
        product_id = int(input("Enter product ID to update: ").strip())
        cur.execute("SELECT product_id, name, quantity, selling_price FROM stock WHERE product_id=%s", (product_id,))
        row = cur.fetchone()
        if not row:
            print("Item not found.")
            cur.close(); conn.close(); return
        name = input(f"New name [{row[1]}]: ").strip() or row[1]
        selling_price_input = input(f"New selling price [{row[3]}]: ").strip()
        selling_price = float(selling_price_input) if selling_price_input != "" else row[3]
        quantity_input = input(f"New quantity [{row[2]}]: ").strip()
        quantity = int(quantity_input) if quantity_input != "" else row[2]
        cur.execute("UPDATE stock SET name=%s, selling_price=%s, quantity=%s WHERE product_id=%s",
                    (name, selling_price, quantity, product_id))
        conn.commit()
        print("Item updated.")
    except ValueError:
        print("Invalid numeric input.")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def delete_stock():
    try:
        conn = get_connection()
        cur = conn.cursor()
        product_id = int(input("Enter product ID to delete: ").strip())
        cur.execute("SELECT product_id FROM stock WHERE product_id=%s", (product_id,))
        if not cur.fetchone():
            print("Item not found.")
            cur.close(); conn.close(); return
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == 'yes':
            cur.execute("DELETE FROM stock WHERE product_id=%s", (product_id,))
            conn.commit()
            print("Deleted.")
        else:
            print("Cancelled.")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def list_stock():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT product_id, name, quantity, selling_price FROM stock ORDER BY product_id")
        rows = cur.fetchall()
        if not rows:
            print("No stock records.")
        else:
            print(f"{'ID':6} {'Name':25} {'Qty':6} {'Rate':10}")
            for r in rows:
                print(f"{r[0]:6} {r[1][:25]:25} {r[2]:6} {format(r[3],'.2f'):10}")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def add_customer():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cu_id = int(input("Enter CU_ID (integer): ").strip())
        cur.execute("SELECT cu_id FROM customer WHERE cu_id=%s", (cu_id,))
        if cur.fetchone():
            print("Customer exists. Use update.")
            cur.close(); conn.close(); return
        name = input("Enter customer name: ").strip()
        mobile = input("Enter mobile number: ").strip()
        cur.execute("INSERT INTO customer (cu_id, name, mobile) VALUES (%s,%s,%s)", (cu_id, name, mobile))
        conn.commit()
        print("Customer added.")
    except ValueError:
        print("Invalid numeric input.")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def update_customer():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cu_id = int(input("Enter CU_ID to update: ").strip())
        cur.execute("SELECT cu_id, name, mobile FROM customer WHERE cu_id=%s", (cu_id,))
        row = cur.fetchone()
        if not row:
            print("Customer not found.")
            cur.close(); conn.close(); return
        name = input(f"New name [{row[1]}]: ").strip() or row[1]
        mobile = input(f"New mobile [{row[2]}]: ").strip() or row[2]
        cur.execute("UPDATE customer SET name=%s, mobile=%s WHERE cu_id=%s", (name, mobile, cu_id))
        conn.commit()
        print("Customer updated.")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def delete_customer():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cu_id = int(input("Enter CU_ID to delete: ").strip())
        cur.execute("SELECT cu_id FROM customer WHERE cu_id=%s", (cu_id,))
        if not cur.fetchone():
            print("Customer not found.")
            cur.close(); conn.close(); return
        confirm = input("Are you sure? (yes/no): ").strip().lower()
        if confirm == 'yes':
            cur.execute("DELETE FROM customer WHERE cu_id=%s", (cu_id,))
            conn.commit()
            print("Deleted.")
        else:
            print("Cancelled.")
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def list_customers():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT cu_id, name, mobile FROM customer ORDER BY cu_id")
        rows = cur.fetchall()
        if not rows:
            print("No customers.")
        else:
            print(f"{'CU_ID':8} {'Name':30} {'Mobile':15}")
            for r in rows:
                print(f"{r[0]:8} {r[1][:30]:30} {r[2]:15}")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def create_new_bill():
    try:
        conn = get_connection()
        cur = conn.cursor()
        bill_no = int(input("Enter Bill No (integer): ").strip())
        cur.execute("SELECT bill_no FROM bills WHERE bill_no=%s", (bill_no,))
        if cur.fetchone():
            print("Bill number exists. Abort.")
            cur.close(); conn.close(); return
        cust_no_input = input("Enter Customer ID (CU_ID) or leave blank for walk-in: ").strip()
        cust_no = int(cust_no_input) if cust_no_input != " "   else None
        if cust_no:
            cur.execute("SELECT cu_id FROM customer WHERE cu_id=%s", (cust_no,))
            if not cur.fetchone():
                print("Customer not found. Create customer first.")
                cur.close(); conn.close(); return
        date_input = input("Bill Date (YYYY-MM-DD) [leave blank for today]: ").strip()
        if date_input == "":
            bill_date = datetime.today().date()
        else:
            try:
                bill_date = datetime.strptime(date_input, "%Y-%m-%d").date()
            except:
                print("Invalid date format.")
                cur.close(); conn.close(); return
        mode = input("Mode of Payment (cash/upi): ").strip().lower()
        if mode not in ('cash', 'upi'):
            print("Mode must be 'cash' or 'upi'.")
            cur.close(); conn.close(); return
        items = []
        while True:
            pid_input = input("Enter Product ID (or type 'done'): ").strip()
            if pid_input.lower() == 'done':
                break
            try:
                pid = int(pid_input)
            except:
                print("Invalid product id.")
                continue
            cur.execute("SELECT name, selling_price, quantity FROM stock WHERE product_id=%s", (pid,))
            s = cur.fetchone()
            if not s:
                print("Product not found.")
                continue
            pname, rate, avail = s
            print(f"Name: {pname} Rate: {format(rate,'.2f')} Available: {avail}")
            try:
                q = int(input("Quantity: ").strip())
            except:
                print("Invalid quantity.")
                continue
            if q <= 0:
                print("Enter positive quantity.")
                continue
            if q > avail:
                print(f"Not enough stock. Available {avail}.")
                continue
            amt = round(float(rate) * q, 2)
            items.append({"product_id": pid, "qty": q, "rate": float(rate), "amount": amt})
            print("Item added.")
        if not items:
            print("No items added. Abort.")
            cur.close(); conn.close(); return
        total = round(sum(i['amount'] for i in items), 2)
        try:
            cur.execute("INSERT INTO bills (bill_no, cust_no, bill_date, mode, total_amount) VALUES (%s,%s,%s,%s,%s)",
                        (bill_no, cust_no, bill_date, mode, total))
            for it in items:
                cur.execute("INSERT INTO bill_items (bill_no, product_id, qty, rate, amount) VALUES (%s,%s,%s,%s,%s)",
                            (bill_no, it['product_id'], it['qty'], it['rate'], it['amount']))
                cur.execute("UPDATE stock SET quantity = quantity - %s WHERE product_id=%s", (it['qty'], it['product_id']))
            conn.commit()
            print("Bill saved.")
            print_bill_formatted(bill_no)
        except Exception as e:
            conn.rollback()
            print("Failed to save bill:", e)
    except ValueError:
        print("Invalid input.")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def print_bill_formatted(bill_no=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        if bill_no is None:
            bill_no = int(input("Enter Bill No to print: ").strip())
        cur.execute("SELECT bill_no, cust_no, bill_date, mode, total_amount FROM bills WHERE bill_no=%s", (bill_no,))
        b = cur.fetchone()
        if not b:
            print("Bill not found.")
            cur.close(); conn.close(); return
        b_bill_no, b_cust_no, b_date, b_mode, b_total = b
        cu_name = "Walk-in"
        cu_mobile = ""
        if b_cust_no:
            cur.execute("SELECT name, mobile FROM customer WHERE cu_id=%s", (b_cust_no,))
            cu = cur.fetchone()
            if cu:
                cu_name, cu_mobile = cu
        cur.execute("SELECT product_id, qty, rate, amount FROM bill_items WHERE bill_no=%s", (bill_no,))
        items = cur.fetchall()
        print("\n" + "="*48)
        print("                   SUPER MARKET BILL")
        print("="*48)
        print(f"Bill No: {b_bill_no}    Date: {b_date}")
        print(f"Customer: {cu_name}    CU_ID: {b_cust_no or '-'}")
        if cu_mobile:
            print(f"Mobile: {cu_mobile}")
        print("-"*48)
        print(f"{'Product':20} {'Qty':>3} {'Rate':>10} {'Amount':>12}")
        print("-"*48)
        for it in items:
            pid, qty, rate, amt = it
            cur.execute("SELECT name FROM stock WHERE product_id=%s", (pid,))
            pr = cur.fetchone()
            pname = pr[0] if pr else str(pid)
            print(f"{pname[:20]:20} {qty:>3} {format(rate,'.2f'):>10} {format(amt,'.2f'):>12}")
        print("-"*48)
        print(f"{'Total':>36} {format(b_total,'.2f'):>12}")
        print(f"Mode: {b_mode}")
        print("="*48 + "\n")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def list_bills():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT bill_no, cust_no, bill_date, mode, total_amount FROM bills ORDER BY bill_date DESC")
        rows = cur.fetchall()
        if not rows:
            print("No bills.")
        else:
            print(f"{'BillNo':8} {'CU_ID':8} {'Date':12} {'Mode':6} {'Total':10}")
            for r in rows:
                print(f"{r[0]:8} {str(r[1] or '-'):8} {r[2]} {r[3]:6} {format(r[4],'.2f'):10}")
    except Exception as e:
        print("Error:", e)
    finally:
        try:
            cur.close(); conn.close()
        except:
            pass

def main_menu():
    create_database_and_tables()

    options = {
        "1": ("Add item to stock", add_stock),
        "2": ("Update stock item", update_stock),
        "3": ("Delete stock item", delete_stock),
        "4": ("List all stock", list_stock),
        "5": ("Add customer", add_customer),
        "6": ("Update customer", update_customer),
        "7": ("Delete customer", delete_customer),
        "8": ("List customers", list_customers),
        "9": ("Create new bill", create_new_bill),
        "10": ("Print/Show bill", print_bill_formatted),
        "11": ("List bills", list_bills),
        "0": ("Exit", None)}

    while True:
        print("\n--- Supermarket Billing System ---")
        for key in ["1","2","3","4","5","6","7","8","9","10","11","0"]:
            text, _ = options[key]
            print(f"{key}. {text}")

        choice = input("Choose option: ").strip()

        if choice == "0":
            print("Goodbye.")
            break

        if choice not in options:
            print("Invalid choice.")
            continue

        func = options[choice][1]
        try:
            func()
        except Exception as e:
            print("ERROR while performing operation:", e)
if __name__ == "__main__":
    main_menu()

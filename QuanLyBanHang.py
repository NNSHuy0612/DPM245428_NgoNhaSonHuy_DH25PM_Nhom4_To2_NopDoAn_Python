import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

# KHAI BÁO VÀ KẾT NỐI CSDL
def connect_db():
    """Hàm kết nối MySQL."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="", # <-- Thay bằng password MySQL của bạn
            database="qlbanhang" 
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi CSDL", f"Lỗi: {err}. Vui lòng kiểm tra MySQL.")
        return None

# HÀM TẢI DỮ LIỆU

san_pham_data = {}

def load_all_data():
    """Tải dữ liệu Sản phẩm từ CSDL và cập nhật Treeview."""
    global san_pham_data
    san_pham_data = {} # Xóa dữ liệu cũ
    
    # Xóa dữ liệu cũ trên Treeview SP
    for item in tree_sp.get_children():
        tree_sp.delete(item)

    conn = connect_db()
    if conn is None: return
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT masp, tensp, giasp, soluongton FROM SanPham")
        rows = cur.fetchall()
        for row in rows:
            masp, tensp, giasp, soluongton = row
            # Lưu dữ liệu vào dictionary để dùng cho chức năng bán hàng
            san_pham_data[masp] = (tensp, giasp, soluongton)
            # Chèn vào Treeview Sản phẩm
            tree_sp.insert("", tk.END, values=row)
            
        # Cập nhật Combobox bán hàng
        combo_sp['values'] = [f"{masp} - {data[0]}" for masp, data in san_pham_data.items()]
        
    except Exception as e:
        messagebox.showerror("Lỗi Tải Dữ Liệu", str(e))
    finally:
        conn.close()

# ====================================================================
# HÀM XỬ LÝ: QUẢN LÝ SẢN PHẨM (CRUD)
# ====================================================================

def clear_input_sp():
    """Xóa nội dung các trường nhập liệu Sản phẩm."""
    entry_ma_sp.config(state='normal')
    entry_ma_sp.delete(0, tk.END)
    entry_ten_sp.delete(0, tk.END)
    entry_gia_sp.delete(0, tk.END)
    entry_soluongton.delete(0, tk.END)

def them_sp():
    """Thêm Sản phẩm mới vào CSDL."""
    masp = entry_ma_sp.get().strip()
    tensp = entry_ten_sp.get().strip()
    giasp = entry_gia_sp.get().strip()
    soluongton = entry_soluongton.get().strip()
    
    if not masp or not tensp or not giasp or not soluongton:
        messagebox.showwarning("Thiếu Dữ Liệu", "Vui lòng nhập đầy đủ Mã, Tên, Giá và Số lượng tồn.")
        return

    conn = connect_db()
    if conn is None: return
    cur = conn.cursor()

    try:
        # Kiểm tra masp trùng
        cur.execute("SELECT masp FROM SanPham WHERE masp = %s", (masp,))
        if cur.fetchone():
             messagebox.showerror("Lỗi Thêm", "Mã Sản phẩm đã tồn tại.")
             return
             
        sql = "INSERT INTO SanPham (masp, tensp, giasp, soluongton) VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (masp, tensp, giasp, soluongton))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã thêm Sản phẩm mới.")
        load_all_data()
        clear_input_sp()
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi Thêm", f"Lỗi MySQL: {err}")
    except Exception as e:
        messagebox.showerror("Lỗi Thêm", str(e))
    finally:
        conn.close()

def sua_sp_select(event):
    """Đổ dữ liệu từ Treeview lên Form để sửa."""
    selected_item = tree_sp.focus()
    if not selected_item: return
    
    values = tree_sp.item(selected_item, 'values')
    if not values: return

    clear_input_sp()
    
    entry_ma_sp.insert(0, values[0]) 
    entry_ten_sp.insert(0, values[1]) 
    entry_gia_sp.insert(0, values[2]) 
    entry_soluongton.insert(0, values[3]) 
    
    entry_ma_sp.config(state='disabled') # Khóa Mã SP khi sửa

def luu_sp():
    """Cập nhật thông tin Sản phẩm (UPDATE)."""
    masp = entry_ma_sp.get() 
    tensp = entry_ten_sp.get().strip()
    giasp = entry_gia_sp.get().strip()
    soluongton = entry_soluongton.get().strip()
    
    if entry_ma_sp.cget('state') != 'disabled' or not masp:
         messagebox.showwarning("Lỗi", "Vui lòng chọn Sản phẩm cần cập nhật.")
         return

    if not tensp or not giasp or not soluongton:
        messagebox.showwarning("Thiếu Dữ Liệu", "Vui lòng nhập đầy đủ thông tin.")
        return
    
    conn = connect_db()
    if conn is None: return
    cur = conn.cursor()

    try:
        sql = """
            UPDATE SanPham 
            SET tensp=%s, giasp=%s, soluongton=%s
            WHERE masp=%s
        """
        cur.execute(sql, (tensp, giasp, soluongton, masp))
        conn.commit()
        messagebox.showinfo("Thành công", f"Đã cập nhật thông tin Sản phẩm có Mã: {masp}.")
        load_all_data()
        clear_input_sp()
    except Exception as e:
        messagebox.showerror("Lỗi Cập Nhật", str(e))
    finally:
        conn.close()

def xoa_sp():
    """Xóa Sản phẩm khỏi CSDL (DELETE)."""
    selected_item = tree_sp.focus()
    if not selected_item:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một Sản phẩm cần xóa.")
        return
    
    masp = tree_sp.item(selected_item, 'values')[0]

    confirm = messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Sản phẩm có Mã: {masp}?")
    if not confirm:
        return

    conn = connect_db()
    if conn is None: return
    cur = conn.cursor()
    
    try:
        sql = "DELETE FROM SanPham WHERE masp=%s"
        cur.execute(sql, (masp,))
        conn.commit()
        messagebox.showinfo("Thành công", "Đã xóa Sản phẩm.")
        load_all_data()
        clear_input_sp()
    except Exception as e:
        messagebox.showerror("Lỗi Xóa", str(e))
    finally:
        conn.close()


# HÀM XỬ LÝ: LẬP ĐƠN HÀNG (BÁN HÀNG)

# Danh sách CTDH tạm thời: [(masp, tensp, giasp, soluong)]
cthd_temp = []

def update_cthd_tree():
    """Cập nhật Treeview Chi tiết Đơn hàng tạm thời và Tổng tiền."""
    for item in tree_cthd.get_children():
        tree_cthd.delete(item)
    
    tong_tien = 0
    for i, item in enumerate(cthd_temp):
        masp, tensp, giasp, soluong = item
        thanh_tien = float(giasp) * int(soluong)
        tong_tien += thanh_tien
        tree_cthd.insert("", tk.END, values=(masp, tensp, f"{giasp:,.0f}", soluong, f"{thanh_tien:,.0f}"))

    lbl_tong_tien.config(text=f"TỔNG THANH TOÁN: {tong_tien:,.0f} VND")

def them_sp_vao_don():
    """Thêm sản phẩm đã chọn vào danh sách tạm thời."""
    
    selected_sp_str = combo_sp.get()
    if not selected_sp_str:
        messagebox.showwarning("Lỗi", "Vui lòng chọn Sản phẩm.")
        return
    
    try:
        # Lấy masp từ chuỗi (ví dụ: "101 - Bánh mì" -> 101)
        masp = int(selected_sp_str.split(' - ')[0])
        soluong = int(entry_soluong_ban.get())
        if soluong <= 0:
             messagebox.showwarning("Lỗi", "Số lượng phải lớn hơn 0.")
             return
    except ValueError:
        messagebox.showerror("Lỗi", "Số lượng không hợp lệ.")
        return

    if masp not in san_pham_data:
        messagebox.showerror("Lỗi", "Sản phẩm không tồn tại.")
        return

    tensp, giasp, soluongton = san_pham_data[masp]
    
    # 1. Kiểm tra tổng số lượng có vượt tồn kho không
    new_soluong = soluong
    found = False
    for i, item in enumerate(cthd_temp):
        if item[0] == masp: 
            new_soluong = item[3] + soluong
            found = True
            break
            
    if new_soluong > soluongton:
         messagebox.showwarning("Lỗi Tồn Kho", f"Số lượng tối đa có thể bán là {soluongton}.")
         return

    # 2. Thêm/Cập nhật vào danh sách tạm thời
    if found:
        cthd_temp[i] = (masp, tensp, giasp, new_soluong)
    else:
        cthd_temp.append((masp, tensp, giasp, soluong))

    update_cthd_tree()
    entry_soluong_ban.delete(0, tk.END)
    entry_soluong_ban.insert(0, "1")

def lap_don_hang():
    """Lưu đơn hàng vào CSDL và cập nhật tồn kho (Khách hàng mặc định: 0/Lẻ)."""
    if not cthd_temp:
        messagebox.showwarning("Lỗi", "Đơn hàng rỗng.")
        return
        
    # Tính tổng tiền
    tong_tien = sum(float(item[2]) * int(item[3]) for item in cthd_temp)

    conn = connect_db()
    if conn is None: return
    cur = conn.cursor()
    
    try:
        
        ngaydat = datetime.now().strftime('%Y-%m-%d')
        
        sql_dh = "INSERT INTO DonHang (ngaydat, tongtien) VALUES (%s, %s)"
        cur.execute(sql_dh, (ngaydat, tong_tien))
        
        madh = cur.lastrowid
        if madh is None:
             raise Exception("Không thể lấy Mã Đơn Hàng mới. Kiểm tra IDENTITY/AUTO_INCREMENT trong CSDL.")
        
        # 2. Thêm vào bảng CTHD và Cập nhật SanPham
        for masp, _, giasp, soluong in cthd_temp:
            # Thêm vào CTHD
            sql_cthd = "INSERT INTO CTHD (madh, masp, soluong, dongia) VALUES (%s, %s, %s, %s)"
            cur.execute(sql_cthd, (madh, masp, soluong, giasp))
            
            # Cập nhật tồn kho SanPham
            sql_update_sp = "UPDATE SanPham SET soluongton = soluongton - %s WHERE masp = %s"
            cur.execute(sql_update_sp, (soluong, masp))
            
        conn.commit()
        messagebox.showinfo("Thành công", f"Đã lập thành công Đơn hàng #{madh}. Tổng tiền: {tong_tien:,.0f} VND")
        
        # 3. Làm mới giao diện
        clear_don_hang()
        load_all_data() # Cập nhật lại tồn kho

    except Exception as e:
        conn.rollback()
        messagebox.showerror("Lỗi Lập Đơn Hàng", str(e))
    finally:
        conn.close()
def xoa_sp_trong_don():
    """Xóa sản phẩm đã chọn khỏi danh sách tạm thời ."""
    selected_item = tree_cthd.focus()
    if not selected_item:
        messagebox.showwarning("Chưa chọn", "Hãy chọn một mục cần xóa khỏi đơn hàng.")
        return
    
    try:
        masp_can_xoa = int(tree_cthd.item(selected_item, 'values')[0])
    except:
        messagebox.showerror("Lỗi", "Không thể lấy mã sản phẩm.")
        return
    
    global cthd_temp
    cthd_temp = [item for item in cthd_temp if item[0] != masp_can_xoa]
    
    update_cthd_tree()
def clear_don_hang():
    """Làm mới giao diện Lập Đơn hàng."""
    global cthd_temp
    cthd_temp = []
    update_cthd_tree()
    entry_soluong_ban.delete(0, tk.END)
    entry_soluong_ban.insert(0, "1")
    

# TKINTER

root = tk.Tk()
root.title("QUẢN LÝ BÁN HÀNG ")
root.geometry("1100x650") 
root.resizable(False, False)
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10, fill="both", expand=True)


#  QUẢN LÝ SẢN PHẨM 
frame_sp = tk.Frame(main_frame, bd=2, relief=tk.GROOVE)
frame_sp.pack(side=tk.LEFT, padx=10, fill="y", expand=False)

tk.Label(frame_sp, text="QUẢN LÝ SẢN PHẨM", font=("Arial", 14, "bold"), fg="navy").pack(pady=10)

# NHẬP THÔNG TIN SP 
frame_input_sp = tk.Frame(frame_sp)
frame_input_sp.pack(pady=5, padx=5, fill="x")

tk.Label(frame_input_sp, text="Mã SP:", width=10).grid(row=0, column=0, padx=5, pady=2, sticky="w")
entry_ma_sp = tk.Entry(frame_input_sp, width=20)
entry_ma_sp.grid(row=0, column=1, padx=5, pady=2, sticky="w")

tk.Label(frame_input_sp, text="Tên SP:", width=10).grid(row=1, column=0, padx=5, pady=2, sticky="w")
entry_ten_sp = tk.Entry(frame_input_sp, width=20)
entry_ten_sp.grid(row=1, column=1, padx=5, pady=2, sticky="w")

tk.Label(frame_input_sp, text="Giá Bán:", width=10).grid(row=2, column=0, padx=5, pady=2, sticky="w")
entry_gia_sp = tk.Entry(frame_input_sp, width=20)
entry_gia_sp.grid(row=2, column=1, padx=5, pady=2, sticky="w")

tk.Label(frame_input_sp, text="Tồn Kho:", width=10).grid(row=3, column=0, padx=5, pady=2, sticky="w")
entry_soluongton = tk.Entry(frame_input_sp, width=20)
entry_soluongton.grid(row=3, column=1, padx=5, pady=2, sticky="w")

# NÚT CHỨC NĂNG 
frame_btn_sp = tk.Frame(frame_sp)
frame_btn_sp.pack(pady=10, padx=5)

tk.Button(frame_btn_sp, text="Thêm", width=10, command=them_sp).grid(row=0, column=0, padx=5)
tk.Button(frame_btn_sp, text="Lưu/Cập nhật", width=12, command=luu_sp).grid(row=0, column=1, padx=5)
tk.Button(frame_btn_sp, text="Làm mới", width=10, command=clear_input_sp).grid(row=0, column=2, padx=5)
tk.Button(frame_btn_sp, text="Xóa", width=10, command=xoa_sp).grid(row=0, column=3, padx=5)

# DANH SÁCH SP
lbl_list_sp = tk.Label(frame_sp, text="Danh sách Sản phẩm", font=("Arial", 10, "bold"))
lbl_list_sp.pack(pady=(5, 2))

tree_frame_sp = tk.Frame(frame_sp)
tree_frame_sp.pack(padx=5, pady=5, fill='both', expand=True)

tree_scroll_sp = ttk.Scrollbar(tree_frame_sp, orient="vertical")
tree_scroll_sp.pack(side="right", fill="y")

tree_sp = ttk.Treeview(tree_frame_sp, columns=("masp", "tensp", "giasp", "soluongton"), show="headings", yscrollcommand=tree_scroll_sp.set)
tree_scroll_sp.config(command=tree_sp.yview)

tree_sp.heading("masp", text="Mã SP")
tree_sp.heading("tensp", text="Tên Sản phẩm")
tree_sp.heading("giasp", text="Giá Bán")
tree_sp.heading("soluongton", text="Tồn Kho")

tree_sp.column("masp", width=60, anchor=tk.CENTER)
tree_sp.column("tensp", width=150)
tree_sp.column("giasp", width=90, anchor=tk.E)
tree_sp.column("soluongton", width=70, anchor=tk.CENTER)

tree_sp.pack(fill="both", expand=True)
tree_sp.bind('<<TreeviewSelect>>', sua_sp_select)

# LẬP ĐƠN HÀNG 
frame_dh = tk.Frame(main_frame, bd=2, relief=tk.GROOVE)
frame_dh.pack(side=tk.LEFT, padx=10, fill="both", expand=True)

tk.Label(frame_dh, text="BÁN HÀNG TẠI QUẦY", font=("Arial", 14, "bold"), fg="darkgreen").pack(pady=10)

# THÊM SẢN PHẨM
frame_add_sp = tk.Frame(frame_dh)
frame_add_sp.pack(pady=5, padx=10, fill="x")

tk.Label(frame_add_sp, text="Chọn SP:", width=10).grid(row=0, column=0, padx=5, pady=5, sticky="w")
combo_sp = ttk.Combobox(frame_add_sp, width=35, state="readonly")
combo_sp.grid(row=0, column=1, padx=5, pady=5, sticky="w")

tk.Label(frame_add_sp, text="SL:", width=5).grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_soluong_ban = tk.Entry(frame_add_sp, width=5)
entry_soluong_ban.insert(0, "1")
entry_soluong_ban.grid(row=0, column=3, padx=5, pady=5, sticky="w")

tk.Button(frame_add_sp, text="➕ Thêm", command=them_sp_vao_don, width=10).grid(row=0, column=4, padx=10, pady=5)

# Sự kiện khi chọn Sản phẩm, hiển thị giá và tồn kho
def on_sp_select(event):
    selected_sp_str = combo_sp.get()
    if not selected_sp_str: return
    try:
        masp = int(selected_sp_str.split(' - ')[0])
        if masp in san_pham_data:
            tensp, giasp, soluongton = san_pham_data[masp]
            lbl_sp_info.config(text=f"Giá: {giasp:,.0f} VND | Tồn: {soluongton}")
        else:
            lbl_sp_info.config(text="Giá: N/A | Tồn: N/A")
    except:
         lbl_sp_info.config(text="Giá: N/A | Tồn: N/A")


combo_sp.bind('<<ComboboxSelected>>', on_sp_select)
lbl_sp_info = tk.Label(frame_add_sp, text="Giá: N/A | Tồn: N/A", fg="gray")
lbl_sp_info.grid(row=1, column=1, padx=5, sticky="w", columnspan=3)

#BẢNG CTDH
lbl_list_cthd = tk.Label(frame_dh, text="CTDH", font=("Arial", 10, "bold"))
lbl_list_cthd.pack(pady=(5, 2))

tree_frame_cthd = tk.Frame(frame_dh)
tree_frame_cthd.pack(padx=10, pady=5, fill='both', expand=True)

tree_scroll_cthd = ttk.Scrollbar(tree_frame_cthd, orient="vertical")
tree_scroll_cthd.pack(side="right", fill="y")

tree_cthd = ttk.Treeview(tree_frame_cthd, columns=("masp", "tensp", "giasp", "soluong", "thanhtien"), show="headings", yscrollcommand=tree_scroll_cthd.set)
tree_scroll_cthd.config(command=tree_cthd.yview)

tree_cthd.heading("masp", text="Mã SP")
tree_cthd.heading("tensp", text="Tên Sản phẩm")
tree_cthd.heading("giasp", text="Đơn Giá")
tree_cthd.heading("soluong", text="Số lượng")
tree_cthd.heading("thanhtien", text="Thành tiền")

tree_cthd.column("masp", width=60, anchor=tk.CENTER)
tree_cthd.column("tensp", width=200)
tree_cthd.column("giasp", width=100, anchor=tk.E)
tree_cthd.column("soluong", width=70, anchor=tk.CENTER)
tree_cthd.column("thanhtien", width=120, anchor=tk.E)

tree_cthd.pack(fill="both", expand=True)

#TỔNG TIỀN
frame_footer_dh = tk.Frame(frame_dh)
frame_footer_dh.pack(pady=10, padx=10, fill="x")
lbl_tong_tien = tk.Label(frame_footer_dh, text="TỔNG THANH TOÁN: 0 VND", font=("Arial", 14, "bold"), fg="red")
lbl_tong_tien.pack(side=tk.LEFT, padx=10)
tk.Button(frame_footer_dh, text=" Xóa SP", width=10,  command=xoa_sp_trong_don).pack(side=tk.RIGHT, padx=5)
tk.Button(frame_footer_dh, text=" Làm mới", width=10, command=clear_don_hang).pack(side=tk.RIGHT, padx=5)
tk.Button(frame_footer_dh, text=" LẬP ĐƠN", width=15, bg="green", fg="white", font=("Arial", 12, "bold"), command=lap_don_hang).pack(side=tk.RIGHT, padx=15)
load_all_data() 

root.mainloop()
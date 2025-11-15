import tkinter as tk
import socket
from datetime import datetime
from tkinter import messagebox
import threading
from tkinter import ttk

window = tk.Tk()
mid_font = ('Noto Sans Mono', 10)
small_font = ('Noto Sans Mono', 8)
height = window.winfo_screenheight()
width = window.winfo_screenwidth()
window.title("Network tools")
# 创建样式对象
style = ttk.Style()
style.configure("Custom.TCombobox", font=mid_font)


def is_port_in_use(port, host='0.0.0.0'):
    # 检测端口是否被占用
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False  # 绑定成功，端口未被占用
        except OSError:
            return True   # 绑定失败，端口已被占用


def run_as_thread(func):  # 装饰器，让函数运行时另开一个线程
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()
    return wrapper


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 连接到一个外部地址（不需要真的连上）
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


local_ip = get_local_ip()
for port in range(8080, 8180):
    if not is_port_in_use(port):
        break


def send_udp_message(message, target_ip, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(code_type.get()), (target_ip, target_port))
    sock.close()


def recv_udp_message(listen_ip='0.0.0.0', listen_port=9999, buffer_size=1024):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((listen_ip, listen_port))
    print(f"正在监听 {listen_ip}:{listen_port} ...")
    data, addr = sock.recvfrom(buffer_size)
    try:
        message = data.decode(code_type.get())
    except UnicodeDecodeError:
        message = data.decode(code_type.get(), errors='replace')
    print(f"收到来自 {addr} 的消息：{message}")
    sock.close()
    return message, addr[0].strip("'").strip("\"")


@run_as_thread
def listen_udp_message():
    listen_port = port
    while True:
        message, addr = recv_udp_message(listen_ip='0.0.0.0', listen_port=listen_port)
        lf2_text1.config(state='normal')
        lf2_text1.insert('end',
                         f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {local_ip}:{listen_port} received from {addr}, protocol: udp, encoding: {code_type.get()}, content:\n{message}\n\n",
                         "red")
        if auto_roll.get() == 1:
            lf2_text1.see(tk.END)  # 自动滚动到底部
        lf2_text1.config(state='disabled')


def send_large_tcp_message(message, target_ip, target_port):
    # 用with的好处是，即使tcp发不出去，也可以自动关闭sock，防止堵塞下一次连接
    with socket.create_connection((target_ip, target_port), timeout=2) as sock:
        sock.sendall(message.encode(code_type.get()))


def recv_large_tcp_message(listen_ip='0.0.0.0', listen_port=9999, buffer_size=4096):
    # 创建 TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((listen_ip, listen_port))
    server.listen(1)
    print(f"正在监听 {listen_ip}:{listen_port} ...")
    conn, addr = server.accept()
    print(f"连接来自：{addr}")
    received_data = b""
    while True:
        chunk = conn.recv(buffer_size)
        if not chunk:
            break
        received_data += chunk
    conn.close()
    server.close()
    try:
        message = received_data.decode(code_type.get())
    except UnicodeDecodeError:
        message = received_data.decode(code_type.get(), errors='replace')
    return message, addr[0].strip("'").strip("\"")


@run_as_thread
def listen_tcp_message():
    listen_port = port
    while True:
        message, addr = recv_large_tcp_message(listen_ip='0.0.0.0', listen_port=listen_port)
        lf2_text1.config(state='normal')
        lf2_text1.insert('end',
                         f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {local_ip}:{listen_port} received from {addr}, protocol: tcp, encoding: {code_type.get()}, content:\n{message}\n\n",
                         "red")
        if auto_roll.get() == 1:
            lf2_text1.see(tk.END)  # 自动滚动到底部
        lf2_text1.config(state='disabled')


# 分为三个模块：网络设置、数据日志（包括收发的信息）、发送信息
'''数据日志'''
labelframe2 = tk.LabelFrame(window, text='数据日志', height=height*4/11, width=width, font=mid_font)
labelframe2.pack()
labelframe2.pack_propagate(0)  # 使组件大小不变


def lf2_reset():
    lf2_text1.config(state='normal')
    lf2_text1.delete('1.0', tk.END)
    lf2_text1.config(state='disabled')


lf2_frm1 = tk.Frame(labelframe2)
lf2_frm1.pack()
auto_roll = tk.IntVar()
auto_roll.set(1)
lf2_cb1 = tk.Checkbutton(lf2_frm1, variable=auto_roll, onvalue=1, offvalue=0, font=mid_font, text='自动滚动')
lf2_cb1.grid(row=1, column=1, padx=width/20)
lf2_button1 = tk.Button(lf2_frm1, text='清空', command=lf2_reset, font=mid_font)
lf2_button1.grid(row=1, column=2, padx=width/20)
lf2_frm2 = tk.Frame(labelframe2)
lf2_frm2.pack(fill=tk.BOTH, expand=True)
lf2_label1 = tk.Label(lf2_frm2, text='')
lf2_label1.pack(side=tk.RIGHT, padx=width/40)  # 控制滚动条的位置用的，不让它太靠近边缘
lf2_scrollbar1 = tk.Scrollbar(lf2_frm2)
lf2_scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
lf2_text1 = tk.Text(lf2_frm2, yscrollcommand=lf2_scrollbar1.set, wrap=tk.WORD, font=small_font)
lf2_text1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
lf2_scrollbar1.config(command=lf2_text1.yview)
lf2_text1.tag_config("red", foreground="red")
lf2_text1.insert('end', '提示：VPN会导致本地主机地址识别不准，关闭VPN后重启软件即可获取正确ip地址\n\n')
lf2_text1.config(state='disabled')


'''发送信息'''
labelframe3 = tk.LabelFrame(window, text='发送信息', height=height*4/11, width=width, font=mid_font)
labelframe3.pack()
labelframe3.pack_propagate(0)  # 使组件大小不变


def lf3_reset():
    lf3_text1.delete('1.0', tk.END)


def lf3_send():
    target_ip = lf1_entry3.get()
    target_port = eval(lf1_entry4.get().strip())
    message = lf3_text1.get(1.0, tk.END).rstrip('\n')
    if message == '':
        messagebox.showerror(title='Cannot send empty message', message='不可发送空白信息')
        return 0
    lf2_text1.config(state='normal')
    lf2_text1.insert('end',
                     f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, {local_ip} sent to {target_ip}:{target_port}, protocol: {prot_type.get()}, encoding: {code_type.get()}, content:\n{message}\nstatus: ?")
    if auto_roll.get() == 1:
        lf2_text1.see(tk.END)  # 自动滚动到底部
    lf2_text1.config(state='disabled')
    window.update()
    try:
        if prot_type.get() == 'udp':
            if len(message.encode(code_type.get())) > 1024:
                messagebox.showerror(title='Message is too large', message='信息大于1024字节，请使用tcp协议发送')
                raise Exception('Message is too large')
            else:
                send_udp_message(message, target_ip, target_port)
        elif prot_type.get() == 'tcp':
            send_large_tcp_message(message, target_ip, target_port)
    except Exception as e:
        print(e)
        lf2_text1.config(state='normal')
        # 删除最后两个字符
        lf2_text1.delete(lf2_text1.index("end-2c"), "end")
        lf2_text1.insert('end', 'failed\n\n')
        lf2_text1.config(state='disabled')
    else:
        lf2_text1.config(state='normal')
        lf2_text1.delete(lf2_text1.index("end-2c"), "end")
        lf2_text1.insert('end', 'succeeded\n\n')
        lf2_text1.config(state='disabled')


lf3_frm1 = tk.Frame(labelframe3)
lf3_frm1.pack(side=tk.RIGHT)
lf3_button2 = tk.Button(lf3_frm1, text='发送', font=mid_font, command=lf3_send)
lf3_button2.pack(pady=height/55)
lf3_button1 = tk.Button(lf3_frm1, text='重置', font=mid_font, command=lf3_reset)
lf3_button1.pack(pady=height/55)
lf3_frm2 = tk.Frame(labelframe3)
lf3_frm2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
lf3_text1 = tk.Text(lf3_frm2, font=mid_font)
lf3_text1.pack(fill=tk.BOTH, expand=True)


'''网络设置'''
labelframe1 = tk.LabelFrame(window, text='网络设置', height=height*3/11, width=width, font=mid_font)
labelframe1.pack()
labelframe1.pack_propagate(0)  # 使组件大小不变
lf1_frm1 = tk.Frame(labelframe1)
lf1_frm1.pack(side=tk.LEFT)
lf1_label1 = tk.Label(lf1_frm1, text='协议类型：', font=mid_font)
lf1_label1.pack()
prot_type = ttk.Combobox(lf1_frm1, values=['udp', 'tcp'], style="Custom.TCombobox", width=8, state="readonly")
prot_type.set('udp')
prot_type.pack()
lf1_label2 = tk.Label(lf1_frm1, text='本地主机地址：', font=mid_font)
lf1_label2.pack()
lf1_entry1 = tk.Entry(lf1_frm1, width=15, font=mid_font)
lf1_entry1.pack()
lf1_entry1.insert('end', local_ip)
lf1_entry1.config(state="readonly")
lf1_label5 = tk.Label(lf1_frm1, text='对方主机地址：', font=mid_font)
lf1_label5.pack()
lf1_entry3 = tk.Entry(lf1_frm1, width=15, font=mid_font)
lf1_entry3.pack()
lf1_entry3.insert('end', '192.168.1.')

lf1_frm2 = tk.Frame(labelframe1)
lf1_frm2.pack(side=tk.RIGHT)
lf1_label4 = tk.Label(lf1_frm2, text='编码方式：', font=mid_font)
lf1_label4.pack()
code_type = ttk.Combobox(lf1_frm2, values=['utf-8', 'gbk'], style="Custom.TCombobox", width=8, state="readonly")
code_type.set('utf-8')
code_type.pack()
lf1_label3 = tk.Label(lf1_frm2, text='本地主机端口：', font=mid_font)
lf1_label3.pack()
lf1_entry2 = tk.Entry(lf1_frm2, width=6, font=mid_font)
lf1_entry2.pack()
lf1_entry2.insert('end', str(port))
lf1_entry2.config(state="readonly")
lf1_label6 = tk.Label(lf1_frm2, text='对方主机端口：', font=mid_font)
lf1_label6.pack()
lf1_entry4 = tk.Entry(lf1_frm2, width=6, font=mid_font)
lf1_entry4.pack()
lf1_entry4.insert('end', '8080')

listen_tcp_message()
listen_udp_message()

window.mainloop()

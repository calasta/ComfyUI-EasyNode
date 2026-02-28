import tkinter as tk
from tkinter import messagebox

def paste_from_clipboard():
    """从剪贴板粘贴内容到输入框"""
    try:
        clipboard_text = root.clipboard_get()
        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", clipboard_text)
    except tk.TclError:
        messagebox.showwarning("警告", "剪贴板中没有可用的文本内容！")

def process_and_copy():
    """将文本转换为特定字典格式并复制回剪贴板"""
    # 获取当前文本
    current_text = text_box.get("1.0", tk.END).strip()
    
    if not current_text:
        messagebox.showwarning("提示", "输入框为空，没有可以处理的内容！")
        return

    # 按行分割文本
    lines = current_text.split('\n')
    
    # 按照要求的格式拼接字符串
    formatted_result = '"": {\n    "positive": (\n'
    
    for line in lines:
        line = line.strip() # 去除每行首尾多余的空格或不可见字符
        if line: # 忽略空行
            # 每行包裹双引号，并加上 \n
            formatted_result += f'        "{line}\\n"\n'
            
    # 补充结尾的部分
    formatted_result += '        "{$@}"\n'
    formatted_result += '        ),\n'
    formatted_result += '    "negative": "{$@}"\n'
    formatted_result += '},'
    
    # 清空并写入剪贴板
    root.clipboard_clear()
    root.clipboard_append(formatted_result)
    root.update()
    
    # 在输入框展示处理后的结果，方便确认
    text_box.delete("1.0", tk.END)
    text_box.insert("1.0", formatted_result)
    
    messagebox.showinfo("成功", "文本已成功转换为字典格式，并已自动复制到剪贴板！")

# --- 主窗口设置 ---
root = tk.Tk()
root.title("字典格式转换工具") # 更新了窗口标题
root.geometry("550x450") # 稍微调大了窗口，因为转换后的代码比较长

# 先把按钮区域固定在窗口底部
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=15)

paste_btn = tk.Button(button_frame, text="粘 贴", width=12, height=1, command=paste_from_clipboard)
paste_btn.pack(side=tk.LEFT, padx=20)

run_btn = tk.Button(button_frame, text="转换并复制", width=12, height=1, command=process_and_copy, bg="#e1f5fe")
run_btn.pack(side=tk.LEFT, padx=20)

# 放置文本框，填满上方剩下的空间
text_box = tk.Text(root, wrap=tk.WORD, font=("Consolas", 10)) # 将字体改为了等宽字体，更适合看代码格式
text_box.pack(padx=10, pady=(10, 0), fill=tk.BOTH, expand=True)

# 启动主循环
root.mainloop()
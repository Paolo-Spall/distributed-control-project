import tkinter as tk

root = tk.Tk()
root.geometry("800x600")

# Top frame
top_frame = tk.Frame(root, bg="red", height=100)
top_frame.pack(side=tk.TOP, fill=tk.X)

# Bottom frame
bottom_frame = tk.Frame(root, bg="blue", height=100)
bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

# Left frame
left_frame = tk.Frame(root, bg="green", width=200)
left_frame.pack(side=tk.LEFT, fill=tk.Y)

# Right frame
right_frame = tk.Frame(root, bg="yellow", width=200)
right_frame.pack(side=tk.RIGHT, fill=tk.Y)

# Center frame
center_frame = tk.Frame(root, bg="white")
center_frame.pack(expand=True, fill=tk.BOTH)

root.mainloop()
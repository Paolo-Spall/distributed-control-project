import tkinter as tk

root = tk.Tk()

# Ottieni la larghezza e l'altezza dello schermo
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Ottieni la scala DPI
dpi_scaling = root.tk.call('tk', 'scaling')

# Calcola la dimensione reale dello schermo
real_screen_width = int(screen_width * dpi_scaling)
real_screen_height = int(screen_height * dpi_scaling)

print(f"Larghezza dello schermo (scalata): {real_screen_width} pixel")
print(f"Altezza dello schermo (scalata): {real_screen_height} pixel")

root.mainloop()
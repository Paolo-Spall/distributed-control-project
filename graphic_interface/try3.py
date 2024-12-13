import tkinter as tk

# Crea la finestra principale
root = tk.Tk()
root.title("Esempio di Casella di Testo")
root.geometry("400x300")

# Crea una casella di testo
text_box = tk.Text(root, wrap=tk.WORD, width=50, height=10)
text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Inserisci del testo nella casella di testo
text_box.insert(tk.END, "Questo è un esempio di casella di testo.\nPuoi scrivere qui.")

# Esegui il loop principale di Tkinter
root.mainloop()
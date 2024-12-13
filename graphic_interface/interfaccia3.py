import tkinter as tk
from tkinter import messagebox, font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image, ImageTk
from functools import partial
import numpy as np
import random
import time


# Percorso all'immagine di sfondo
image_path = "grass.png"

# Lista per memorizzare i punti della route disegnata
points = []
info_points = []  # Lista per salvare i dati degli info point


# Flag per tracciare lo stato del disegno
drawing = False

#FLag route scarta o no
discard_route = False

# Condizioni meteo possibili
weather_conditions = ["Sunny", "Cloudy", "Rainy", "Windy"]

# Aggiungi simboli per le condizioni meteo
weather_symbols = {
    "Sunny": "☀️",
    "Cloudy": "☁️",
    "Rainy": "🌧️",
    "Windy": "💨",
}

danger_symbol = {
    "Danger": "⚠"
}

text_font = ("Arial", 15)

def error_message():
    # Crea una finestra figlia indipendente
    window = tk.Toplevel(root)
    window.title("ERROR: Situation that needs human intervention")
    window.geometry("400x250")
    window.configure(bg="lightgray")
    
    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    
    # Lista di errori casuali
    errors = [
        "One sheep undetectable, \n contact support (Help)",
        "Storm incoming, \n bring back your sheep (Task Manager)",
        "Dangerous animal detected, \n bring back your sheep (Task Manager)",
        "One drone discharged, \n bring back your sheep (Task Manager)",
        "One robotic dog discharged,\n bring back your sheep (Task Manager)",
        "One drone lost, \n contact support (Help)"
    ]
    selected_error = errors[random.randint(0, len(errors) - 1)]
    
    # Icona di avviso
    icon_label = tk.Label(window, text="⚠️", font=("Arial", 40), bg="lightgray", fg="red")
    icon_label.pack(pady=10)
    
    # Messaggio di errore
    error_label = tk.Label(
        window,
        text=f"Error: {selected_error}",
        font=("Arial", 14, "bold"),
        bg="lightgray",
        fg="black",
        wraplength=350,
        justify="center"
    )
    error_label.pack(pady=10)
    # if random.randint(0, 20) == 2:
    #     delay_time = 10  # Tempo di ritardo in secondi
    #     threading.Timer(delay_time, error_message).start()
    
    # Pulsante per chiudere la finestra
    close_button = tk.Button(
        window,
        text="Close",
        font=("Arial", 14),
        bg="red",
        fg="white",
        command=window.destroy  # Distrugge solo la finestra di errore
    )
    close_button.pack(pady=20)
    
    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

def disable_button(button, color):
    button.config(state=tk.DISABLED, bg=color)

def enable_button(button, color):
    button.config(state=tk.NORMAL, bg=color)

def enable_drawing():
    canvas.mpl_connect("button_press_event", on_mouse_press)
    canvas.mpl_connect("motion_notify_event", on_mouse_move)
    canvas.mpl_connect("button_release_event", on_mouse_release)

# Funzione per bloccare il disegno
def disable_drawing():
    canvas.mpl_disconnect(canvas.mpl_connect("button_press_event", on_mouse_press))
    canvas.mpl_disconnect(canvas.mpl_connect("motion_notify_event", on_mouse_move))
    canvas.mpl_disconnect(canvas.mpl_connect("button_release_event", on_mouse_release))


# Funzione per aprire una finestra di informazioni
def show_info_window(point_number, sheep_count, danger_level):
    
    # Salva i dettagli nella lista e nel file di testo
    info = (
        f"Point {point_number}:\n"
        f"  Sheep Count: {sheep_count}\n"
        #f"  Danger Level: {danger_level}\n"
        f"  Weather: {initial_weather}\n"
    )
    info_points.append(info)
    
    # Scrive il punto nel file di testo
    with open("route_report.txt", "a") as file:
        file.write(info + "\n")

# Funzione per inizializzare il messaggio di "Design the route"
def show_weather_top_interface():
    message_label.config(
        text=(
            f"Date: 2024-12-25      Time: 10:00       Weather: {initial_weather}       Temperature: {initial_temperature}°C "
            )
        )


# Funzione per tracciare il percorso come spezzata chiusa
def plot_path(points, finished=False):
    ax.cla()
    ax.imshow(img, extent=[0, img.shape[1], 0, img.shape[0]])
    ax.set_xlim(0, img.shape[1])
    ax.set_ylim(0, img.shape[0])
    #ax.invert_yaxis()

    if len(points) > 1:
        if finished:
            points.append(points[0])  # Chiude il percorso
        x, y = zip(*points)
        # x = list(x) + [x[0]]  # Chiude il percorso
        # y = list(y) + [y[0]]
        ax.plot(x, y, color='blue', marker='o', linewidth=2, zorder=1)

    canvas.draw()

# Funzione per aggiungere un punto in base all'evento del mouse
def add_point(event):
    if event.inaxes:
        x, y = event.xdata, event.ydata
        if 0 <= x <= img.shape[1] and 0 <= y <= img.shape[0]:
            points.append((x, y))
            plot_path(points)


# Funzione per gestire il click del mouse (inizio disegno)
def on_mouse_press(event):
    global drawing
    drawing = True
    points.clear()
    add_point(event)


# Funzione per gestire il movimento del mouse (disegno continuo)
def on_mouse_move(event):
    if drawing:
        add_point(event)

# Funzione per gestire il rilascio del mouse (ferma il disegno)
def on_mouse_release(event):
    global drawing
    drawing = False
    plot_path(points, finished=True)
    draw_end_message()
    disable_drawing()
    set_default_cursor()
    enable_button(start_button, "green")


# Funzione per generare un percorso geometrico chiuso alternativo
def generate_closed_random_route():
    center_x, center_y = img.shape[1] / 2, img.shape[0] / 2
    num_sides = random.randint(3, 6)
    radius = min(img.shape[1], img.shape[0]) / 3
    random_route = []

    for i in range(num_sides):
        angle = 2 * np.pi * i / num_sides
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        random_route.append((x, y))

    return random_route

# Funzione per ottenere una durata e condizioni meteo casuali
def get_random_duration_weather():
    duration = round(random.uniform(7.5, 8.5), 2)
    hours = int(duration)
    minutes = int((duration - hours) * 60)
    duration_str = f"{hours} hours and {minutes} minutes"
    weather = random.choice(weather_conditions)
    return duration, duration_str, weather, hours, minutes

def get_random_initial_weather():
    weather = random.choice(list(weather_symbols.keys()))  # Condizione meteo casuale
    temperature = random.randint(0, 20)  # Temperatura casuale tra 0°C e 20°C
    return weather, temperature

# Funzione per salvare i punti del percorso in un file di testo
def save_path():
    try:
        save_location = "path_points.txt"
        with open(save_location, "w") as file:
            for point in points:
                file.write(f"{point[0]}, {point[1]}\n")
        #messagebox.showinfo("Route saved", f"Route saved in {save_location}")
    except Exception as e:
        messagebox.showerror("Saving error", f"I was unable to save the file: {e}")

def save_final_report():
    final_message = (
        "\nFinal Report:\n"
        "The route has been completed successfully.\n"
        "The flock is re-entered in the sheepfold.\n"
        "Information about the route\n")
    with open("route_report.txt", "a") as file:
        file.write(final_message)
    messagebox.showinfo("Route completed!!", "The flock is re-entered in the sheepfold and \n "
                                             "the final report has been saved as 'route_report.txt'.")


# Funzione per evidenziare la traccia esistente
def highlight_trace(points, color='red', total_time=5):

    points = np.array(points)

    n_points = len(points)
    real_time = 6#0

    lengths = []
    tot_length = 0.
    for i in range(1, n_points):
        length = np.linalg.norm(points[i] - points[i-1])
        lengths.append(length)

        tot_length += length

    nd = 100
    dl = tot_length / nd

    x_int = np.array([])
    y_int=np.array([])
    
    for i in range(1, n_points):
        nn = round(lengths[i-1] / dl)
        xx = np.linspace(points[i-1][0],points[i][0],  nn)
        yy = np.linspace(points[i-1][1],points[i][1],  nn)
        x_int = np.concatenate((x_int, xx))
        y_int = np.concatenate((y_int, yy))

    delay = real_time / (nd + 1)
    pecora_img = plt.imread('pecora1.png')
    pecora_dim = 25
    wait = time.time()
    for i in range(len(x_int)):
        a = ax.imshow(pecora_img, extent=[x_int[i]-pecora_dim, x_int[i]+pecora_dim, y_int[i]-pecora_dim,  y_int[i]+pecora_dim], zorder=3)
        ax.plot(x_int[:i], y_int[:i], color=color, linewidth=2, zorder=2)
        canvas.draw()
        canvas.get_tk_widget().update()
        time.sleep(delay)
        a.remove()
        if time.time()-wait > random.randrange(25, 40):
            error_message()
            wait = time.time()
            # delay_time = 10  # Tempo di ritardo in secondi
            # threading.Timer(delay_time, error_message).start()
            
    
    ax.plot([points[-1][0], points[0][0]], [points[-1][1], points[0][1]], color=color, marker='o', linewidth=2)
    canvas.draw()
    time.sleep(delay)

#Funzione per gestire il click sul pulsante "Fatto"
def on_start(side_frame):
    global discard_route
    global points
    global current_weather, initial_temperature
    duration_str, weather, temperature, hours, minutes = get_random_duration_weather()
    weather = initial_weather  # Usa lo stesso meteo iniziale
    temperature = initial_temperature  # Usa la stessa temperatura iniziale
    total_time = hours * 60 + minutes

    # horizontal_frame.destroy()


    text = (
            "\n"
            "Grazing activity is in progress.\n\n"
            "Start time: 10:00\n"
            "Expected return time: 18:23\n\n"
            "No anomalies detected.\n"

    )

    # Etichetta per il secondo messaggio
    info_label = tk.Label(side_frame, text=text, width=30,  wraplength=250, justify=tk.LEFT, font=text_font, bg="white")
    info_label.pack(pady=10)
    disable_button(start_button, "lightgreen")
    enable_button(program_overview_button, "pink")
    enable_button(task_manager_button, "yellow")
    highlight_trace(points, total_time=total_time)
    save_final_report()
    enable_drawing()
    disable_button(task_manager_button, "lightyellow")
    set_pencil_cursor()
    final_text = (
        "\n\n"
        "Grazing activity is over.\n\n"
        "You can draw a new route\n"
    )
    info_label = tk.Label(side_frame, text=final_text, width=30,  wraplength=250, justify=tk.LEFT, font=text_font, bg="white")
    info_label.pack(pady=10)

def on_help():
    # Crea una finestra figlia indipendente
    window = tk.Toplevel(root)
    window.title("Help")
    window.geometry("600x300")
    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    
    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Aggiungere scritte
    info_label = tk.Label(window, justify=tk.LEFT, font=("Arial", 14), bg="white")
    info_label.pack(pady=10)

    user_manual_button = tk.Button(window, text="User Manual", command=on_user_manual, height=4, width=10, font=("Arial", 20), bg="lightblue", fg="black")
    user_manual_button.pack(side=tk.LEFT, pady=10, padx=10, expand=True, fill=tk.BOTH, anchor=tk.CENTER)

    # chat_button = tk.Button(window, text="Chat", command=on_chat, height=4, width=10, bg="lightblue", fg="black")
    # chat_button.pack(side=tk.LEFT, pady=10, padx=10,expand=True, fill=tk.BOTH, anchor=tk.CENTER)
    
    contact_button = tk.Button(window, text="Contacts", command=on_contacts, height=4, width=10, font=("Arial", 20), bg="lightblue", fg="black")
    contact_button.pack(side=tk.LEFT, pady=10, padx=10,expand=True, fill=tk.BOTH, anchor=tk.CENTER)

def on_weather():
    # Crea una finestra figlia indipendente
    window = tk.Toplevel(root)
    window.title("Utils")
    window.geometry("600x600")
    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    weather_text = ("\nENVIRONMENT CONDITION:\n\n"
                    "📅: 2024-12-25\n"
            "🕒 : 10:00 \n"
            f"🌥: {initial_weather}\n"
            f"🌡: {initial_temperature}°C\n\n"
            "No significant weather changes are anticipated in the next hours.\n"
            "\n\n FLEET STATUS:\n\n"
            "Drone 1 battery: 100%\n"
            "Drone 2 battery: 98%\n"
            "Drone 3 battery: 100%\n"
            "Drone 4 battery: 97%\n"
            "Drone 5 battery: 100%\n\n"
            "Robotic dog 1 battery: 100%\n"
            "Robotic dog 2 battery: 96%\n"
            "Robotic dog 3 battery: 99%\n"
            "Robotic dog 4 battery: 95%\n"
            "Robotic dog 5 battery: 100%\n"
            "Robotic dog 6 battery: 100%\n\n"
        )
    
    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Aggiungere scritte
    info_label = tk.Label(window, text=weather_text, justify=tk.LEFT, font=("Arial", 14), bg="white")
    info_label.pack(pady=10)

    # Aggiungi un pulsante per chiudere la finestra
    close_button = tk.Button(window, text="Close", font=("Arial", 14), command=window.destroy)
    close_button.pack(pady=10)

def on_user_manual():

    window = tk.Toplevel(root)
    window.title("Help")
    window.geometry("800x500")
    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    user_text = ("Browse the user manual to get detailed instructions on how to use the system.\n"
        )
    
    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Aggiungere scritte
    info_label = tk.Label(window, text=user_text, justify=tk.LEFT, font=("Arial", 14), bg="white")
    info_label.pack(pady=10)

    try:
        # Apre il file di testo in modalità lettura
        with open('user_manual.txt', 'r') as file:
            manuale = file.read()  # Legge tutto il contenuto del file
        
        # # Aggiungere scritte
        # info_label = tk.Label(window, text=manuale, justify=tk.LEFT, font=("Arial", 14), bg="white")
        # info_label.pack(pady=10)
        
        # Crea un widget Text per mostrare il manuale
        text_widget = tk.Text(window, wrap='word', height=20, width=60)
        text_widget.pack(padx=20, pady=20)
        
        # Inserisci il contenuto del manuale nel widget Text
        text_widget.insert(tk.END, manuale)
        
        # Disabilita la modifica del testo
        text_widget.config(state=tk.DISABLED)
        
        # Aggiungi un pulsante per chiudere la finestra
        close_button = tk.Button(window, text="Close",font=("Arial", 14), command=window.destroy)
        close_button.pack(pady=10)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def on_contacts():
    window = tk.Toplevel(root)
    window.title("Contacts")
    window.geometry("600x300")
    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    contact_text = ("You can contact assistance at the following references:\n"
        "Phone: 1234567890\n"
        "Email: sheperding.service@gmail.com\n"
        "Chat: www.sheperding.service.it\n"
        )
    
    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Aggiungere scritte
    info_label = tk.Label(window, text=contact_text, justify=tk.LEFT, font=("Arial", 14), bg="white")
    info_label.pack(pady=10)

    # Aggiungi un pulsante per chiudere la finestra
    close_button = tk.Button(window, text="Close", font=("Arial", 14), command=window.destroy)
    close_button.pack(pady=10)

def initial_message():
    window = tk.Toplevel(root)
    window.title("Draw the route")
    window.geometry("700x450+300+200")
    window.configure(bg="lightgray")

    # Testo del messaggio
    message = (
        "Click on the map to draw your route:\n"
        "Hold down the left mouse button pressed and drag it in the green window.\n"
    )

    # Label per visualizzare il messaggio
    label = tk.Label(window, text=message, bg="lightgray", justify="left", font=("Arial", 12))
    label.pack(padx=20, pady=20)

    # Carica e visualizza la GIF
    gif_path = "immagine_iniziale.gif"  # Sostituisci con il percorso della tua GIF
    gif = Image.open(gif_path)

    # Convertiamo la GIF in un formato compatibile con Tkinter
    frames = []
    for frame in range(gif.n_frames):
        gif.seek(frame)
        frame_image = ImageTk.PhotoImage(gif.copy())  # Converti in PhotoImage
        frames.append(frame_image)

    # Funzione per animare la GIF
    def animate_gif(index=0):
        gif_label.config(image=frames[index])  # Aggiorna l'immagine
        window.after(100, animate_gif, (index + 1) % len(frames))  # Passa al prossimo frame

    # Label per la GIF
    gif_label = tk.Label(window, bg="lightgray")
    gif_label.pack(pady=10)

    # Inizia l'animazione
    animate_gif()
    
    show_again_var = tk.BooleanVar(value=True)  # Di default è spuntata

    # Checkbox per "Don't show it again"
    checkbox = tk.Checkbutton(
        window,
        text="Don't show it again",
        variable=show_again_var,
        bg="lightgray",
        font=("Arial", 10),
        anchor="e"
    )
    checkbox.pack(side="bottom", pady=10)

    # Pulsante "I understand"
    button = tk.Button(window, text="I understand", command=window.destroy, font=("Arial", 16)) 
    button.pack(pady=10)

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()

def on_task_manager():
    global screen_width
    global screen_height
    # Crea una finestra figlia indipendente
    window = tk.Toplevel(root)
    window.title("Task manager", )
    window.geometry(f"{round(screen_width / 2.5)}x{round(screen_height / 2.5)}")

    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    

    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")


    user_manual_button = tk.Button(window, text="Bring back the flock", command=partial(on_bring_back, window),
                                   height=4, width=10, font=("Arial", 20),bg="lightblue", fg="black")
    user_manual_button.pack(side=tk.LEFT, pady=10, padx=10, expand=True, fill=tk.BOTH, anchor=tk.CENTER)

    # chat_button = tk.Button(window, text="Chat", command=on_chat, height=4, width=10, bg="lightblue", fg="black")
    # chat_button.pack(side=tk.LEFT, pady=10, padx=10,expand=True, fill=tk.BOTH, anchor=tk.CENTER)

    contact_button = tk.Button(window, text="Pause the pasture", command=partial(on_pause, window), height=4, width=10,
                               font=("Arial", 20), bg="lightblue", fg="black")
    contact_button.pack(side=tk.LEFT, pady=10, padx=10, expand=True, fill=tk.BOTH, anchor=tk.CENTER)

def on_pause(old_window):
    global thread_flag
    thread_flag = True
    old_window.destroy()
    global screen_width
    global screen_height
    # Crea una finestra figlia indipendente
    window = tk.Toplevel(root)
    window.title("Stop", )
    window.geometry(f"{round(screen_width / 2.5)}x{round(screen_height / 2.5)}")

    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    help_text = ("Click to resume the pasture")

    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Aggiungere scritte
    info_label = tk.Label(window, text=help_text, justify=tk.LEFT, font=("Arial", 14), bg="white")
    info_label.pack(pady=10)

    # Aggiungi un pulsante per chiudere la finestra
    close_button = tk.Button(window, text="Resume",font=("Arial", 14), command=window.destroy)
    close_button.pack(pady=10)

    # contact_button = tk.Button(window, text="Resume", command=partial(on_resume, window), height=4, width=10, bg="lightblue", fg="black")
    # contact_button.pack(side=tk.LEFT, pady=10, padx=10, fill=tk.BOTH, anchor=tk.CENTER)

def on_resume(old_window):
    pause_flag = False
    old_window.destroy()

def on_bring_back(old_window):
    old_window.destroy()
    global screen_width
    global screen_height
    # Crea una finestra figlia indipendente
    window = tk.Toplevel(root)
    window.title("Stop", )
    window.geometry(f"{round(screen_width / 2.5)}x{round(screen_height / 2.5)}")

    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    help_text = ("The pasture is headed back to the sheepfold")

    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Aggiungere scritte
    info_label = tk.Label(window, text=help_text, justify=tk.LEFT, font=("Arial", 14), bg="white")
    info_label.pack(pady=10)

    # Aggiungi un pulsante per chiudere la finestra
    close_button = tk.Button(window, text="Ok",font=("Arial", 18), width = 4, height = 2, command=window.destroy)
    close_button.pack(pady=10)

def on_quit_program():
    """Crea una finestra figlia che permette di confermare l'uscita dal programma."""
    global screen_width
    global screen_height

    # Crea la finestra figlia
    window = tk.Toplevel(root)
    window.title("Quit program")
    window.geometry("400x200")  # Dimensioni predefinite
    window.configure(bg="white")

      # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Impedisce l'interazione con la finestra principale
    window.transient(root)
    window.grab_set()

    # Testo nella finestra figlia
    contact_text = "Click 'Ok' to abort the program."

    # Etichetta con il testo
    info_label = tk.Label(window, text=contact_text, justify=tk.CENTER, font=("Arial", 14), bg="white")
    info_label.pack(pady=20)

    # Pulsante per chiudere il programma
    close_button = tk.Button(window, text="Ok",font=("Arial", 18), width = 4, height = 2, command=lambda: close_program(window))
    close_button.pack(pady=10)

def close_program(window):
    """Chiude la finestra figlia e termina l'intero programma."""
    window.destroy()  # Chiude la finestra di conferma
    root.quit()  # Termina il ciclo principale di Tkinter
    root.destroy()  # Chiude la finestra principale

def on_further_info():
    window = tk.Toplevel(root)
    window.title("Program Overview")
    window.geometry("600x600")
    window.configure(bg="white")

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()
    contact_text = ("GRAZE ACTIVITY SUMMARY INFO:\n\n"
        "Sheep in the flock: 20\n"
        "Sheep retrieved: 0\n"
        "Sheep lost: 0\n"
        "Sheep in danger: 0\n\n"
        "Number of chasing dogs: 0\n"
        "Formation dogs: 6\n"
        "Formations executed: exagonal, pentagonal \n\n"
        "Coverage area: 1 [km^2]\n"
        "Drones altitude: 20 [m]\n\n"
        "Path traveled: 17.6 [km]\n"
        "Shepherding time: 4 hours and 23 minutes\n"
        "Distance from the sheepfold: 5 [km]\n"
        "Maximum chasing distance: 50 [m]\n\n"
        "Average speed of the flock: 3.8 [km/h]\n"
        "Average rate of chasing modality: 0.6\n"
        
        )
    
    # Centrare la finestra
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    position_top = (screen_height // 2) - (window_height // 2)
    position_right = (screen_width // 2) - (window_width // 2)
    window.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Aggiungere scritte
    info_label = tk.Label(window, text=contact_text, justify=tk.LEFT, font=("Arial", 14), bg="white")
    info_label.pack(pady=10)

    # Aggiungi un pulsante per chiudere la finestra
    close_button = tk.Button(window, text="Close", font=("Arial", 14), command=window.destroy)
    close_button.pack(pady=10)
    
def set_pencil_cursor():
    canvas.get_tk_widget().config(cursor="pencil")

def set_default_cursor():
    canvas.get_tk_widget().config(cursor="arrow")

def draw_end_message():
    window = tk.Toplevel(root)
    window.title("Draw the route")
    window.geometry("300x200+500+400")
    window.configure(bg="lightgray")

    # Testo del messaggio
    message = (
        "Well done! The route is designed.\n"
        "Send the drones to check the path? .\n"
    )

    # Label per visualizzare il messaggio
    label = tk.Label(window, text=message, bg="lightgray", justify="left", font=("Arial", 12))
    label.pack(padx=20, pady=20)

    # Creazione del frame per i pulsanti
    button_frame = tk.Frame(window, bg="lightgray")
    button_frame.pack(pady=20)

    # Pulsante "Continue"
    button_continue = tk.Button(button_frame, text="Check", command=lambda: drones_check(window),
                                font=("Arial", 12))
    button_continue.grid(row=0, column=0, padx=20)  # Posiziona il primo pulsante con uno spazio a destra

    # Pulsante "Redo"
    button_redo = tk.Button(button_frame, text="Re-design", command=lambda: redo_command(window), font=("Arial", 12))
    button_redo.grid(row=0, column=1, padx=20)  # Posiziona il secondo pulsante con uno spazio a sinistra

    # Impedisce che altre interazioni avvengano nella finestra principale
    window.transient(root)
    window.grab_set()

#Conferma che la traccia è stata disegnata correttamente
def continue_command(old_window=None):
    if old_window:
        old_window.destroy()

    new_window = tk.Toplevel(root)
    new_window.title("Draw the route")
    new_window.geometry("650x200+400+250")
    new_window.configure(bg="lightgray")

    # Testo del messaggio
    message = (
        "Now that the path is ready, press Start  to launch the program.\n"
    )
    # Label per visualizzare il messaggio
    label = tk.Label(new_window, text=message, bg="lightgray", justify="left", font=("Arial", 12))
    label.pack(padx=20, pady=20)

    # Pulsante "I understand"
    button = tk.Button(new_window, text="I understand",command=new_window.destroy, font=("Arial", 18))
    button.pack(pady=10)

    # Impedisce che altre interazioni avvengano nella finestra principale
    new_window.transient(root)
    new_window.grab_set()

def redo_command(window):
    window.destroy()
    points.clear()
    info_points.clear()
    enable_drawing()
    set_pencil_cursor()


def drones_check(old_window):
    old_window.destroy()
    global discard_route
    discard_route = random.choice([True, False, False, False, False, False])
    #discard_route = random.choice([True,True])

    if discard_route:
        window = tk.Toplevel(root)
        window.title("Route Control")
        window.geometry("450x200+500+400")
        window.configure(bg="lightgray")

        # Testo del messaggio
        message = (
            "The drones didn't accept the route.They propose a new route,\n"
            "do you want to accept it or re-draw the route?\n"
        )

        # Label per visualizzare il messaggio
        label = tk.Label(window, text=message, bg="lightgray", justify="left", font=("Arial", 12))
        label.pack(padx=20, pady=20)

        # Creazione del frame per i pulsanti
        button_frame = tk.Frame(window, bg="lightgray")
        button_frame.pack(pady=20)

        # Pulsante accept modify by the drones
        button_accept = tk.Button(button_frame, text="Accept drone's route", command=lambda: accept_command(window),
                                  font=("Arial", 12))
        button_accept.grid(row=0, column=0, padx=20)  # Posiziona il secondo pulsante con uno spazio a sinistra

        # Pulsante "Redraw"
        button_redraw = tk.Button(button_frame, text="Redo", command=lambda: redo_command(window),
                                  font=("Arial", 12))
        button_redraw.grid(row=0, column=1, padx=20)  # Posiziona il primo pulsante con uno spazio a destra

        # Impedisce che altre interazioni avvengano nella finestra principale
        window.transient(root)
        window.grab_set()
    else:
        continue_command()

def accept_command(window):
    global points
    points = generate_closed_random_route()
    plot_path(points, finished=True)
    continue_command(window)


# Carica l'immagine di sfondo
img = mpimg.imread(image_path)

# Finestra principale di Tkinter
root = tk.Tk()
root.title("Automated Sheperding System")   

# # Imposta la finestra a schermo intero
# root.attributes("-fullscreen", True)

# Configura la chiusura della finestra
root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())


uns_screen_width = root.winfo_screenwidth()
uns_screen_height = root.winfo_screenheight()
# Ottieni la scala DPI
dpi_scaling = root.tk.call('tk', 'scaling') 

# Calcola la dimensione reale dello schermo
screen_width = int(uns_screen_width * dpi_scaling)
screen_height = int(uns_screen_height * dpi_scaling)

root.state('zoomed')

# Set the size of the main window
#root.geometry(f"{screen_width}x{screen_height}")  # Width x Height


# Crea il frame laterale con altezza limitata a metà della schermata
horizontal_frame = tk.Frame(root, height=5, bg="white")
horizontal_frame.pack(side=tk.TOP, fill=tk.X, padx=0)

# Etichetta per i messaggi dinamici
message_label = tk.Label(horizontal_frame, text="", font=("Arial", 14), wraplength=1000, justify=tk.LEFT, bg="white")
message_label.pack(side=tk.TOP, fill=tk.X, padx=30)

# Meteo iniziale
initial_weather, initial_temperature = get_random_initial_weather()


side_frame = tk.Frame(root, bg="white", bd=2, relief="solid", width=screen_width//5)
side_frame.pack(fill=tk.Y, side=tk.RIGHT, padx=10, pady=10)


# Frame inferiore per il pulsante--> pulsanti in basso
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.LEFT, fill=tk.Y)

##########################################
#PULSANTI

large_font = font.Font(size=screen_height//40)
medium_font = font.Font(size=screen_height//50)

# Pulsante Utils
weather_button = tk.Button(bottom_frame, text="Utils", command=on_weather, bg="lightblue",
                           fg="black", font = large_font)  # , font=("Arial", 20))
weather_button.pack(side=tk.BOTTOM,pady=30,padx=20, expand=True, fill=tk.BOTH, anchor=tk.CENTER)

# Pulsante Task Manager
task_manager_button = tk.Button(bottom_frame, text="Task Manager", command=on_task_manager, bg="yellow",
                        fg="black", font = large_font)
task_manager_button.pack(side=tk.BOTTOM, pady=30,padx=20, expand=True, fill=tk.BOTH, anchor=tk.CENTER)

disable_button(task_manager_button, "lightyellow")

# Pulsante Program Overview
program_overview_button = tk.Button(side_frame, text="Activity Overview", command=on_further_info,  bg="pink",
                        fg="black", font = large_font)
program_overview_button.pack(side=tk.BOTTOM, pady=10, padx=10, anchor=tk.CENTER)
disable_button(program_overview_button, "lightpink")


# Pulsante Start
start_button = tk.Button(bottom_frame, text="Start", command=partial(on_start, side_frame),  bg="green", fg="black", font = large_font)
start_button.pack(side=tk.BOTTOM,pady=30,padx=20, expand=True, fill=tk.BOTH, anchor=tk.CENTER)

disable_button(start_button, "lightgreen")


# Pulsante Help
help_button = tk.Button(bottom_frame, text="Help", command=on_help,  bg="lightblue", fg="black", font = medium_font)
help_button.pack(side=tk.LEFT, pady=30, padx=5, expand=True, fill=tk.BOTH, anchor='ne')


# Pulsante quit
quit_button = tk.Button(bottom_frame, text="Quit", command=on_quit_program,  bg="red", fg="black", font=medium_font)
quit_button.pack(side=tk.LEFT,pady=30,padx=5, expand=True, fill=tk.BOTH, anchor='nw')




##########################################
#Creazione mappa

#frame per la mappa
map_frame_width = round(screen_width)

right_frame = tk.Frame(root, width=map_frame_width, bg="white")
right_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

# Mostra il messaggio iniziale
initial_message()


# Crea una figura Matplotlib per la mappa
fig, ax = plt.subplots()
ax.imshow(img, extent=[0, img.shape[1], 0, img.shape[0]])
ax.set_xlim(0, img.shape[1])
ax.set_ylim(0, img.shape[0])

# Collega il grafico Matplotlib al frame inferiore e posizionalo con place
canvas = FigureCanvasTkAgg(fig, master=right_frame)

 
canvas.get_tk_widget().place(x=0, y=0, width=round(screen_width*0.56), height=round(screen_height*0.9))

# Configura la chiusura della finestra
root.protocol("WM_DELETE_WINDOW", lambda: root.destroy())

#Mostra il messaggio iniziale
show_weather_top_interface()

#cursore matita
set_pencil_cursor()

# Collega gli eventi del mouse--> attiva il trascinamento sull'immagine
enable_drawing()

#Mantieni attiva l'interfaccia
root.mainloop()

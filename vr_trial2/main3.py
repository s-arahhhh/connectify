from vidstream import *
import tkinter as tk 
import socket
import threading

local_ip_address = socket.gethostbyname(socket.gethostname())

server = StreamingServer(local_ip_address, 7777)
receiver = AudioReceiver(local_ip_address, 6666)

def start_listening():
    t1 = threading.Thread(target=server.start_server)
    t2 = threading.Thread(target=receiver.start_server)
    t1.start()
    t2.start()

def start_camera_stream():
    camera_client = CameraClient(text_target_ip.get(1.0,'end-1c'), 9999)
    t3 = threading.Thread(target=camera_client.start_stream)
    t3.start()

def start_screen_sharing():
    screen_client = ScreenShareClient(text_target_ip.get(1.0,'end-1c'), 9999)
    t4 = threading.Thread(target=screen_client.start_stream)
    t4.start()

def start_audio_stream():
    audio_sender = AudioSender(text_target_ip.get(1.0,'end-1c'), 8888)
    t5 = threading.Thread(target=audio_sender.start_stream)
    t5.start()

# Chat functionality
def send_message():
    message = text_chat_input.get("1.0", 'end-1c')
    if message:
        text_chat_log.config(state=tk.NORMAL)
        text_chat_log.insert(tk.END, f"You: {message}\n")
        text_chat_log.config(state=tk.DISABLED)
        text_chat_input.delete("1.0", tk.END)
        with open("chat_log.txt", "a") as file:
            file.write(f"You: {message}\n")

# Whiteboard functionality
def paint(event):
    x1, y1 = (event.x - 1), (event.y - 1)
    x2, y2 = (event.x + 1), (event.y + 1)
    canvas.create_oval(x1, y1, x2, y2, fill="black", width=2)

# GUI with grid layout
window = tk.Tk()
window.title("Connectify Virtual Room")
window.geometry('500x800')

label_target_ip = tk.Label(window, text="Target IP:")
label_target_ip.grid(row=0, column=0, padx=10, pady=10)

text_target_ip = tk.Text(window, height=1, width=30)
text_target_ip.grid(row=0, column=1, padx=10, pady=10)

btn_listen = tk.Button(window, text="Start Listening", width=30, command=start_listening)
btn_listen.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

btn_camera = tk.Button(window, text="Start Camera Stream", width=30, command=start_camera_stream)
btn_camera.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

btn_screen = tk.Button(window, text="Start Screen Sharing", width=30, command=start_screen_sharing)
btn_screen.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

btn_audio = tk.Button(window, text="Start Audio Stream", width=30, command=start_audio_stream)
btn_audio.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Chatbox
label_chat_log = tk.Label(window, text="Chat:")
label_chat_log.grid(row=5, column=0, padx=10, pady=10)

text_chat_log = tk.Text(window, height=10, width=50, state=tk.DISABLED)
text_chat_log.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

text_chat_input = tk.Text(window, height=2, width=30)
text_chat_input.grid(row=7, column=0, padx=10, pady=10)

btn_send_message = tk.Button(window, text="Send", command=send_message)
btn_send_message.grid(row=7, column=1, padx=10, pady=10)

# Whiteboard
label_whiteboard = tk.Label(window, text="Whiteboard:")
label_whiteboard.grid(row=8, column=0, padx=10, pady=10)

canvas = tk.Canvas(window, bg='white', height=200, width=400)
canvas.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
canvas.bind("<B1-Motion>", paint)

window.mainloop()

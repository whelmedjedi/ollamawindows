import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import subprocess

import ollama

# Global variables for chat messages
messages = []

def send_message(chat_input):
    global messages

    messages.append({
        'role': 'user',
        'content': chat_input,
    })

    update_chat_history()  # Update chat display immediately

    # Start thread to send message and get response
    thread = threading.Thread(target=process_response, args=(chat_input,))
    thread.start()

def process_response(chat_input):
    global messages

    # Call the Llama chat model
    stream = ollama.chat(
        model='llama3',
        messages=messages,
        stream=True,
    )

    response = ""
    for chunk in stream:
        part = chunk['message']['content']
        response += part

    # Append AI's response to messages list
    messages.append({
        'role': 'assistant',
        'content': response,
    })

    update_chat_history()  # Update chat display with AI's response

def update_chat_history():
    global chat_text
    chat_text.config(state=tk.NORMAL)
    chat_text.delete(1.0, tk.END)
    
    for message in messages:
        role = message['role']
        content = message['content']
        background_color = '#2B2B2B'  # Dark background color for messages
        text_color = 'white'  # Text color for messages

        if role == 'user':
            chat_text.tag_configure('user_message', justify='right', background='#80CBC4', foreground='black')
            chat_text.insert(tk.END, f'You: {content}\n', 'user_message')
        elif role == 'assistant':
            chat_text.tag_configure('assistant_message', justify='left', background='#FFC107', foreground='black')
            chat_text.insert(tk.END, f'Jarvis: {content}\n', 'assistant_message')
        
        # Apply background color to the message text
        chat_text.tag_add('background', f'{chat_text.index(tk.END)}-2c', tk.END)  # Move to the start of the message
        chat_text.tag_configure('background', background=background_color, foreground=text_color)

    chat_text.config(state=tk.DISABLED)
    chat_text.see(tk.END)

def send_question(event=None):
    user_input = input_text.get("1.0", tk.END).strip()
    if user_input:
        send_message(user_input)
        input_text.delete("1.0", tk.END)

def run_llama3_command():
    try:
        subprocess.Popen(['ollama', 'run', 'llama3'])
    except Exception as e:
        print(f"Error running command: {e}")

def stop_ollama_process():
    try:
        # Execute PowerShell command to stop the 'ollama' process
        subprocess.Popen(['powershell', 'Get-Process | Where-Object {$_.ProcessName -like \'*ollama*\'} | Stop-Process'])
    except Exception as e:
        print(f"Error stopping ollama process: {e}")

# Function to apply text highlighting to selected text
def highlight_selected_text(event):
    chat_text.tag_remove('highlight', '1.0', tk.END)  # Remove existing highlighting

    try:
        sel_start = chat_text.index(tk.SEL_FIRST)
        sel_end = chat_text.index(tk.SEL_LAST)
        chat_text.tag_add('highlight', sel_start, sel_end)
    except tk.TclError:
        pass  # No selection or invalid selection range

# Create GUI
root = tk.Tk()
root.title("Jarvis")  # Set the title of the window

# Configure grid layout
root.columnconfigure(0, weight=1)  # Main column (for chat and prompt) expands horizontally
root.columnconfigure(1, weight=0)  # Column 1 (for buttons) does not expand

root.rowconfigure(0, weight=1)      # Row 0 (chat display) expands both horizontally and vertically
root.rowconfigure(1, weight=1)      # Row 1 (input and buttons) does not expand

# Chat display area (on the left)
chat_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=('Segoe UI', 12), bg="#2B2B2B", fg="white", padx=10, pady=10)
chat_text.grid(row=0, column=0, sticky="nsew")  # Use grid layout for chat display
chat_text.config(state=tk.DISABLED)  # Disable editing of chat text
chat_text.bind('<ButtonRelease-1>', highlight_selected_text)  # Bind mouse release event to highlight selected text

# User input entry (on the left)
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=('Segoe UI', 12), bg="#2B2B2B", fg="white", padx=10, pady=10)
input_text.grid(row=1, column=0, sticky="nsew")  # Use grid layout for user input, stretch horizontally and fill vertically

# Frame for right-side navigation bar
nav_frame = tk.Frame(root)
nav_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")  # Place navigation frame in the right column

# Send button (styled)
send_button = ttk.Button(nav_frame, text="Send", command=send_question, style='TButton')
send_button.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Use pack layout for Send button, expand to fill available space

# Run 'ollama run llama3' button (styled)
run_ollama_button = ttk.Button(nav_frame, text="Start Jarvis", command=run_llama3_command, style='TButton')
run_ollama_button.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Use pack layout for Run button, expand to fill available space

# Stop 'ollama' process button (styled)
stop_ollama_button = ttk.Button(nav_frame, text="Stop Jarvis", command=stop_ollama_process, style='TButton')
stop_ollama_button.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Use pack layout for Stop button, expand to fill available space

# Configure text tag for highlighting
chat_text.tag_configure('highlight', background='lightblue')

# Function to execute when closing the window
def on_closing():
    stop_ollama_process()  # Stop the 'ollama' process when closing the window
    root.destroy()         # Close the tkinter application

# Register the on_closing function to be called when the window is closed
root.protocol("WM_DELETE_WINDOW", on_closing)

# Bind Enter key to send_question function
input_text.bind('<Return>', send_question)

# Start GUI main loop
root.mainloop()

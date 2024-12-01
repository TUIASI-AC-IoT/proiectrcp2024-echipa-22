# Server (server.py)
import socket
import time
import psutil
import struct
import tkinter as tk
from tkinter import ttk
import threading


class MonitoringServer:
    def __init__(self):
        self.hostname = "Default"  # Valoare implicită
        self.running = False
        self.server_socket = None

    def set_hostname(self, hostname):
        self.hostname = hostname

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('', 4533))

            group = socket.inet_aton('224.0.0.251')
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.server_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            self.running = True

            while self.running:
                try:
                    data, addr = self.server_socket.recvfrom(1024)
                    if not self.running:
                        break
                    metric_type = data.decode().strip()

                    if metric_type == "Discover":
                        response = f"Server {self.hostname} active"
                    else:
                        metric_value = self.get_metric(metric_type)
                        response = f"{metric_value} - from {self.hostname}"

                    self.server_socket.sendto(response.encode(), addr)
                except Exception as e:
                    if not self.running:
                        break
                    print(f"Error handling request: {e}")
                    continue

        except Exception as e:
            if self.running:
                print(f"Server error: {e}")
        finally:
            if self.server_socket:
                try:
                    self.server_socket.close()
                except:
                    pass

    def stop_server(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.sendto("SERVER_STOPPING".encode(), ('224.0.0.251', 4533))
                time.sleep(0.5)
                self.server_socket.close()
            except:
                pass


class ServerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitoring Server")
        self.server = MonitoringServer()
        self.server_thread = None
        self.setup_gui()

    def setup_gui(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Adăugăm câmp pentru hostname
        ttk.Label(frame, text="Hostname:").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.hostname_entry = ttk.Entry(frame)
        self.hostname_entry.grid(row=0, column=1, pady=5, padx=5)
        self.hostname_entry.insert(0, self.server.hostname)

        ttk.Label(frame, text="Port: 4533").grid(row=1, column=0, columnspan=2, pady=5)

        self.status_var = tk.StringVar(value="Server oprit")
        ttk.Label(frame, textvariable=self.status_var).grid(row=2, column=0, columnspan=2, pady=5)

        self.toggle_button = ttk.Button(frame, text="Start Server", command=self.toggle_server)
        self.toggle_button.grid(row=3, column=0, columnspan=2, pady=5)

    def toggle_server(self):
        if self.toggle_button["text"] == "Start Server":
            # Actualizăm hostname-ul înainte de pornirea serverului
            self.server.set_hostname(self.hostname_entry.get())
            self.hostname_entry.config(state='disabled')  # Dezactivăm modificarea în timp ce serverul rulează

            self.server_thread = threading.Thread(target=self.server.start_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.status_var.set("Server pornit")
            self.toggle_button["text"] = "Stop Server"
        else:
            self.server.stop_server()
            if self.server_thread:
                self.server_thread.join(timeout=1)
            self.status_var.set("Server oprit")
            self.toggle_button["text"] = "Start Server"
            self.hostname_entry.config(state='normal')  # Reactivăm modificarea hostname-ului

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.server.stop_server()
        self.root.destroy()


if __name__ == "__main__":
    gui = ServerGUI()
    gui.run()
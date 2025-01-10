import socket
import time
import psutil
import struct
import threading
import tkinter as tk
from tkinter import ttk

class MonitoringServer:
    def __init__(self):
        self.hostname = "Default"
        self.running = False
        self.server_socket = None
        self.ttl = 120  # TTL implicit

    def set_hostname(self, hostname):
        self.hostname = hostname

    def set_ttl(self, ttl):
        self.ttl = ttl

    def get_metric(self, metric_type):
        try:
            if metric_type == "CPU":
                return f"{psutil.cpu_percent(interval=0.1)}%"
            elif metric_type == "Memory":
                return f"{psutil.virtual_memory().percent}%"
            elif metric_type == "Disk":
                return f"{psutil.disk_usage('/').percent}%"
            elif metric_type == "Network":
                net = psutil.net_io_counters()
                return f"Sent={net.bytes_sent}B Recv={net.bytes_recv}B"
            elif metric_type == "CPU Temperature":
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps and 'coretemp' in temps:
                        return f"{temps['coretemp'][0].current}\u00b0C"
                return "N/A"
        except Exception as e:
            return f"Error: {str(e)}"
        return "Invalid metric"

    def create_dns_sd_response(self, metric_type, metric_value):
        srv_record = f"_monitoring._udp.local {self.hostname} {4533}"
        txt_record = f"metric={metric_type},value={metric_value}"
        ptr_record = f"_monitoring._udp.local {self.hostname}"
        return srv_record, txt_record, ptr_record

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
                        srv_record, txt_record, ptr_record = self.create_dns_sd_response(metric_type, metric_value)
                        response = f"SRV: {srv_record}\nTXT: {txt_record}\nPTR: {ptr_record}"

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

        ttk.Label(frame, text="Hostname:").grid(row=0, column=0, pady=5, sticky=tk.W)
        self.hostname_entry = ttk.Entry(frame)
        self.hostname_entry.grid(row=0, column=1, pady=5, padx=5)
        self.hostname_entry.insert(0, self.server.hostname)

        ttk.Label(frame, text="TTL:").grid(row=1, column=0, pady=5, sticky=tk.W)
        self.ttl_entry = ttk.Entry(frame)
        self.ttl_entry.grid(row=1, column=1, pady=5, padx=5)
        self.ttl_entry.insert(0, str(self.server.ttl))

        self.status_var = tk.StringVar(value="Server oprit")
        ttk.Label(frame, textvariable=self.status_var).grid(row=2, column=0, columnspan=2, pady=5)

        self.toggle_button = ttk.Button(frame, text="Start Server", command=self.toggle_server)
        self.toggle_button.grid(row=3, column=0, columnspan=2, pady=5)

    def toggle_server(self):
        if self.toggle_button["text"] == "Start Server":
            self.server.set_hostname(self.hostname_entry.get())
            try:
                ttl = int(self.ttl_entry.get())
                if ttl <= 0:
                    raise ValueError("TTL trebuie sa fie pozitiv.")
                self.server.set_ttl(ttl)
            except ValueError as e:
                self.status_var.set(f"Eroare TTL: {str(e)}")
                return

            self.hostname_entry.config(state='disabled')
            self.ttl_entry.config(state='disabled')

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
            self.hostname_entry.config(state='normal')
            self.ttl_entry.config(state='normal')

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.server.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    gui = ServerGUI()
    gui.run()

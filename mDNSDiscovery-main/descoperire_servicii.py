#descoperire_servicii
import socket
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import time
import threading
import struct


class MonitoringClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(2)

    def send_request(self, metric_type):
        try:
            self.socket.sendto(metric_type.encode(), ('224.0.0.251', 4533))
            data, addr = self.socket.recvfrom(1024)
            return data.decode(), addr
        except socket.timeout:
            return "Server unavailable", None
        except Exception as e:
            return f"Error: {str(e)}", None

    def close(self):
        try:
            self.socket.close()
        except:
            pass


class ServiceDiscovery:
    def __init__(self, services_frame, metrics_frame):
        self.services_listbox = None
        self.metrics_history = None
        self.setup_gui_elements(services_frame, metrics_frame)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1)
        self.running = False
        self.server_stopped = False
        self.reconnect_delay = 2  # seconds between reconnection attempts
        self.last_server_check = 0

        # Flag pentru a indica dacă încercăm să ne reconectăm
        self.attempting_reconnection = False

        self.setup_monitor_socket()

        self.metrics = ["CPU", "Memory", "Disk", "Network", "CPU Temperature"]
        self.last_metric_request = 0
        self.metric_interval = 15

    def setup_gui_elements(self, services_frame, metrics_frame):
        ttk.Label(metrics_frame, text="Metrics History").pack()
        self.metrics_history = tk.Text(metrics_frame, width=80, height=15)
        self.metrics_history.pack(fill=tk.BOTH, expand=True)

    def setup_monitor_socket(self):
        try:
            self.monitor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.monitor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.monitor_socket.settimeout(1)
            self.monitor_socket.bind(('', 4533))
            group = socket.inet_aton('224.0.0.251')
            mreq = struct.pack('4sL', group, socket.INADDR_ANY)
            self.monitor_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            print("Monitor socket setup successfully")
        except Exception as e:
            print(f"Error setting up monitor socket: {e}")
            self.monitor_socket = None

    def check_server_status(self):
        """Verifică dacă serverul este disponibil"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            test_socket.settimeout(1)
            test_socket.sendto("Discover".encode(), ('224.0.0.251', 4533))
            data, addr = test_socket.recvfrom(1024)
            test_socket.close()
            return True
        except:
            return False

    def attempt_reconnection(self):
        """Încearcă reconectarea la server"""
        if self.check_server_status():
            print("Server detected - reconnecting...")
            self.server_stopped = False
            self.attempting_reconnection = False

            # Recreează socketurile
            try:
                self.socket.close()
            except:
                pass
            try:
                self.monitor_socket.close()
            except:
                pass

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1)
            self.setup_monitor_socket()

            self.append_metric("Reconnected to server!\n")
            return True
        return False

    def discover(self):
        self.running = True
        while self.running:
            try:
                if self.server_stopped:
                    time.sleep(self.reconnect_delay)
                    continue
                self.socket.sendto("Discover".encode(), ('224.0.0.251', 4533))
                data, addr = self.socket.recvfrom(1024)
                if addr[0] == '224.0.0.251':
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    response = f"{timestamp} - Service: {data.decode()} at {addr[0]}:{addr[1]}"
                    self.services_listbox.after(0, self.update_services_list, response)
            except socket.timeout:
                pass
            except Exception as e:
                print(f"Discovery error: {e}")
            time.sleep(2)

    def monitor_metrics(self):
        while self.running:
            current_time = time.time()

            # Verifică starea serverului și încearcă reconectarea dacă e necesar
            if self.server_stopped and current_time - self.last_server_check > self.reconnect_delay:
                self.last_server_check = current_time
                if not self.attempting_reconnection:
                    self.attempting_reconnection = True
                    self.append_metric("Attempting to reconnect to server...\n")
                if self.attempt_reconnection():
                    continue

            if self.server_stopped:
                time.sleep(1)
                continue

            try:
                if not self.monitor_socket:
                    self.setup_monitor_socket()
                    if not self.monitor_socket:
                        time.sleep(1)
                        continue

                data, addr = self.monitor_socket.recvfrom(1024)
                if not self.running:
                    break

                message = data.decode().strip()
                if message == "SERVER_STOPPING":
                    self.server_stopped = True
                    self.attempting_reconnection = False
                    self.append_metric("Server has stopped. Waiting for reconnection...\n")
                    continue

                metric_type = message
                if metric_type != "Discover":
                    try:
                        response_data, addr = self.monitor_socket.recvfrom(1024)
                        response_text = response_data.decode()

                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        formatted_message = f"{timestamp} - {response_text} (from {addr[0]}:{addr[1]})\n"

                        self.metrics_history.after(0, self.append_metric, formatted_message)

                    except socket.timeout:
                        continue

            except socket.timeout:
                continue
            except Exception as e:
                if not self.running:
                    break
                print(f"Monitoring error: {e}")
                if "Bad file descriptor" in str(e):
                    self.setup_monitor_socket()
                time.sleep(1)

    def update_services_list(self, response):
        self.services_listbox.insert(tk.END, response)
        self.services_listbox.see(tk.END)
        if self.services_listbox.size() > 5:
            self.services_listbox.delete(0)

    def append_metric(self, message):
        self.metrics_history.insert(tk.END, message)
        self.metrics_history.see(tk.END)

        content = self.metrics_history.get("1.0", tk.END).splitlines()
        if len(content) > 20:
            self.metrics_history.delete("1.0", tk.END)
            self.metrics_history.insert(tk.END, "\n".join(content[-20:]) + "\n")

    def stop(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass
        try:
            self.monitor_socket.close()
        except:
            pass
        self.server_stopped = True


class ClientGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Monitoring Client")
        self.client = MonitoringClient()
        self.setup_gui()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        services_frame = ttk.LabelFrame(main_frame, text="Active Services", padding="15")
        services_frame.grid(row=0, column=0, rowspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))

        metrics_frame = ttk.LabelFrame(main_frame, text="Resource Metrics", padding="5")
        metrics_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        self.resource_labels = {}
        self.metrics = {
            "CPU": tk.BooleanVar(value=True),
            "Memory": tk.BooleanVar(value=True),
            "Disk": tk.BooleanVar(value=True),
            "Network": tk.BooleanVar(value=True),
            "CPU Temperature": tk.BooleanVar(value=True)
        }

        for i, metric in enumerate(self.metrics):
            frame = ttk.Frame(services_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)

            ttk.Checkbutton(frame, text=metric, variable=self.metrics[metric]).pack(side=tk.LEFT)
            value_label = ttk.Label(frame, text="No data")
            value_label.pack(side=tk.RIGHT)
            self.resource_labels[metric] = value_label

        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttl_frame = ttk.Frame(right_frame)
        ttl_frame.grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(ttl_frame, text="TTL:").pack(side=tk.LEFT)
        self.ttl_entry = ttk.Entry(ttl_frame, width=10)
        self.ttl_entry.pack(side=tk.LEFT, padx=5)
        self.ttl_entry.insert(0, "120")

        self.response_text = tk.Text(right_frame, wrap=tk.WORD, height=15, width=50)
        self.response_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        button_frame = ttk.Frame(right_frame)
        button_frame.grid(row=2, column=0, sticky=tk.W, pady=5)

        ttk.Button(button_frame, text="Submit",
                   command=self.submit_request).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export to File",
                   command=self.export_to_file).pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(right_frame, text="")
        self.status_label.grid(row=3, column=0, sticky=tk.W, pady=5)

        self.discovery = ServiceDiscovery(services_frame, metrics_frame)

        self.discovery_thread = threading.Thread(target=self.discovery.discover)
        self.discovery_thread.daemon = True
        self.discovery_thread.start()

        self.monitor_thread = threading.Thread(target=self.discovery.monitor_metrics)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def update_resource_label(self, metric, value):
        if metric in self.resource_labels:
            self.resource_labels[metric].config(text=value)

    def submit_request(self):
        if self.discovery.server_stopped:
            messagebox.showwarning("Avertisment", "Serverul este oprit! Așteptați reconectarea.")
            return

        selected_metrics = [metric for metric, var in self.metrics.items() if var.get()]

        if not selected_metrics:
            messagebox.showwarning("Avertisment", "Selectați cel puțin o resursă!")
            return

        try:
            ttl = int(self.ttl_entry.get())
            if ttl <= 0:
                raise ValueError("TTL trebuie să fie pozitiv")
        except ValueError as e:
            messagebox.showerror("Eroare", f"Valoare TTL invalidă: {str(e)}")
            return

        for metric in selected_metrics:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.status_label.config(text=f"Trimitere solicitare pentru {metric}...")
            self.root.update()

            response, addr = self.client.send_request(metric)

            if response == "Server unavailable":
                self.update_resource_label(metric, "Server offline")
                self.response_text.insert(tk.END,
                                          f"{timestamp} - Server offline pentru {metric}\n")
            elif response and addr:
                value = response.split(" - from")[0]
                self.update_resource_label(metric, value)
                self.response_text.insert(tk.END,
                                          f"{timestamp} - {response} (from {addr[0]}:{addr[1]})\n")
            else:
                self.update_resource_label(metric, "Error")
                self.response_text.insert(tk.END,
                                          f"{timestamp} - Eroare pentru {metric}\n")

            self.response_text.see(tk.END)
            self.root.update()
            time.sleep(0.1)

        self.status_label.config(text="Configurare finalizată!")

    def export_to_file(self):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"resource_data_{timestamp}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.response_text.get("1.0", tk.END))
            messagebox.showinfo("Succes", f"Datele au fost exportate în fișierul: {filename}")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la exportul datelor: {str(e)}")

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.client.close()
        self.discovery.stop()
        self.root.destroy()


if __name__ == "__main__":
    gui = ClientGUI()
    gui.run()
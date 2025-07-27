#!/usr/bin/env python3
"""
Comprehensive Demo System
Demonstrates all components of the AI Dreaming system
"""

import subprocess
import time
import threading
import tkinter as tk
from tkinter import messagebox
import webbrowser
from pathlib import Path


class DemoLauncher:
    """Launcher for demonstrating the complete AI system"""
    
    def __init__(self):
        self.processes = {}
        self.root = tk.Tk()
        self.root.title("🧠 AI Dreaming System - Demo Launcher")
        self.root.geometry("600x700")
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the demo launcher GUI"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🧠 AI Dreaming System", 
                             font=('Arial', 20, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(title_frame, text="Autonomous Multi-Agent Thinking Platform", 
                                font=('Arial', 12), fg='#ecf0f1', bg='#2c3e50')
        subtitle_label.pack()
        
        # Main content
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # System Overview
        overview_frame = tk.LabelFrame(main_frame, text="System Overview", 
                                     font=('Arial', 12, 'bold'), padx=10, pady=10)
        overview_frame.pack(fill=tk.X, pady=(0, 15))
        
        overview_text = """This system demonstrates autonomous AI thinking through:

• Single-agent autonomous reasoning (DreamingAI)
• Multi-agent conversations without system prompts
• Real-time GUI monitoring and visualization
• Web-based conversation monitoring
• AI-generated conversation highlights
• Web search integration for informed thinking"""
        
        tk.Label(overview_frame, text=overview_text, justify=tk.LEFT, 
                font=('Arial', 10)).pack(anchor=tk.W)
        
        # Demo Components
        demo_frame = tk.LabelFrame(main_frame, text="Demo Components", 
                                 font=('Arial', 12, 'bold'), padx=10, pady=10)
        demo_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Component buttons
        components = [
            ("🤖 Single Agent Dreaming", "Launch autonomous reasoning", self.launch_single_agent),
            ("👥 Multi-Agent Conversations", "Start agent conversations", self.launch_multi_agent),
            ("📊 GUI Visualizer", "Real-time conversation GUI", self.launch_gui),
            ("🌐 Web Monitor", "Web-based monitoring", self.launch_web_monitor),
            ("🔍 Web Search Demo", "Search-integrated thinking", self.launch_search_demo),
            ("📋 System Test", "Test all components", self.run_system_test)
        ]
        
        for title, description, command in components:
            self.create_demo_button(demo_frame, title, description, command)
        
        # Status and Controls
        status_frame = tk.LabelFrame(main_frame, text="System Status", 
                                   font=('Arial', 12, 'bold'), padx=10, pady=10)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_text = tk.Text(status_frame, height=8, font=('Courier', 9))
        scrollbar = tk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(control_frame, text="Clear Status", command=self.clear_status,
                 bg='#3498db', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(control_frame, text="Stop All", command=self.stop_all_processes,
                 bg='#e74c3c', fg='white', font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(control_frame, text="Exit Demo", command=self.exit_demo,
                 bg='#95a5a6', fg='white', font=('Arial', 10)).pack(side=tk.RIGHT)
        
        # Initial status
        self.log_status("🚀 Demo launcher ready!")
        self.log_status("📖 Select a component above to begin demonstration")
    
    def create_demo_button(self, parent, title, description, command):
        """Create a demo component button"""
        button_frame = tk.Frame(parent, relief=tk.RAISED, borderwidth=1)
        button_frame.pack(fill=tk.X, pady=5)
        
        # Main button
        btn = tk.Button(button_frame, text=title, command=command,
                       bg='#2ecc71', fg='white', font=('Arial', 11, 'bold'),
                       height=2, relief=tk.FLAT)
        btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Description
        tk.Label(button_frame, text=description, font=('Arial', 10),
                fg='#7f8c8d').pack(side=tk.LEFT, padx=(10, 5), pady=5)
    
    def log_status(self, message):
        """Log a status message"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def clear_status(self):
        """Clear status log"""
        self.status_text.delete(1.0, tk.END)
    
    def launch_single_agent(self):
        """Launch single agent dreaming system"""
        self.log_status("🤖 Launching single agent dreaming system...")
        try:
            process = subprocess.Popen(['python3', 'dreaming_ai.py'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            self.processes['single_agent'] = process
            self.log_status("✅ Single agent system started (check terminal)")
        except Exception as e:
            self.log_status(f"❌ Failed to start single agent: {e}")
    
    def launch_multi_agent(self):
        """Launch multi-agent conversation system"""
        self.log_status("👥 Launching multi-agent conversation system...")
        try:
            process = subprocess.Popen(['python3', 'multi_agent_system.py'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            self.processes['multi_agent'] = process
            self.log_status("✅ Multi-agent system started (check terminal)")
        except Exception as e:
            self.log_status(f"❌ Failed to start multi-agent system: {e}")
    
    def launch_gui(self):
        """Launch GUI visualizer"""
        self.log_status("📊 Launching GUI visualizer...")
        try:
            process = subprocess.Popen(['python3', 'gui_visualizer.py'])
            self.processes['gui'] = process
            self.log_status("✅ GUI visualizer started")
        except Exception as e:
            self.log_status(f"❌ Failed to start GUI: {e}")
    
    def launch_web_monitor(self):
        """Launch web monitoring interface"""
        self.log_status("🌐 Launching web monitoring interface...")
        try:
            process = subprocess.Popen(['python3', 'web_monitor.py'])
            self.processes['web_monitor'] = process
            self.log_status("✅ Web monitor started")
            
            # Wait a moment then open browser
            def open_browser():
                time.sleep(3)
                self.log_status("🌐 Opening browser to http://localhost:8080")
                webbrowser.open('http://localhost:8080')
            
            threading.Thread(target=open_browser, daemon=True).start()
            
        except Exception as e:
            self.log_status(f"❌ Failed to start web monitor: {e}")
    
    def launch_search_demo(self):
        """Launch web search demonstration"""
        self.log_status("🔍 Running web search integration demo...")
        try:
            process = subprocess.Popen(['python3', 'web_search_agent.py'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            # Read output in real-time
            def read_output():
                for line in process.stdout:
                    self.root.after(0, self.log_status, f"🔍 {line.strip()}")
                process.wait()
                self.root.after(0, self.log_status, "🔍 Search demo completed")
            
            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            self.log_status(f"❌ Failed to run search demo: {e}")
    
    def run_system_test(self):
        """Run comprehensive system test"""
        self.log_status("📋 Running comprehensive system test...")
        
        def test_sequence():
            # Test 1: Check Python files exist
            required_files = [
                'dreaming_ai.py', 'multi_agent_system.py', 'gui_visualizer.py',
                'web_monitor.py', 'web_search_agent.py'
            ]
            
            for file in required_files:
                if Path(file).exists():
                    self.root.after(0, self.log_status, f"✅ Found {file}")
                else:
                    self.root.after(0, self.log_status, f"❌ Missing {file}")
            
            # Test 2: Check dependencies
            try:
                import requests
                self.root.after(0, self.log_status, "✅ requests library available")
            except ImportError:
                self.root.after(0, self.log_status, "❌ requests library missing")
            
            try:
                import flask
                self.root.after(0, self.log_status, "✅ flask library available")
            except ImportError:
                self.root.after(0, self.log_status, "❌ flask library missing")
            
            try:
                import tkinter
                self.root.after(0, self.log_status, "✅ tkinter available")
            except ImportError:
                self.root.after(0, self.log_status, "❌ tkinter missing")
            
            # Test 3: Check Ollama API (optional)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    self.root.after(0, self.log_status, f"✅ Ollama API responding ({len(models)} models)")
                else:
                    self.root.after(0, self.log_status, "⚠️ Ollama API not responding")
            except:
                self.root.after(0, self.log_status, "⚠️ Ollama API not available (optional)")
            
            self.root.after(0, self.log_status, "📋 System test completed!")
        
        threading.Thread(target=test_sequence, daemon=True).start()
    
    def stop_all_processes(self):
        """Stop all running processes"""
        self.log_status("🛑 Stopping all processes...")
        for name, process in self.processes.items():
            try:
                process.terminate()
                self.log_status(f"🛑 Stopped {name}")
            except:
                pass
        self.processes.clear()
    
    def exit_demo(self):
        """Exit the demo launcher"""
        self.stop_all_processes()
        self.root.quit()
    
    def run(self):
        """Run the demo launcher"""
        self.root.protocol("WM_DELETE_WINDOW", self.exit_demo)
        self.root.mainloop()


def main():
    """Main entry point for demo system"""
    print("🧠 AI Dreaming System - Demo Launcher")
    print("=" * 50)
    print("Starting GUI launcher...")
    
    launcher = DemoLauncher()
    launcher.run()


if __name__ == "__main__":
    main()
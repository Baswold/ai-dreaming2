#!/usr/bin/env python3
"""
Tkinter GUI for real-time visualization of agent conversations
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sqlite3
import json
import requests
from datetime import datetime
from pathlib import Path


class AgentConversationGUI:
    """GUI application for visualizing agent conversations"""
    
    def __init__(self, db_path: str = "multi_agent_memory.db"):
        self.db_path = db_path
        self.root = tk.Tk()
        self.root.title("🤖 Multi-Agent Conversation Visualizer")
        self.root.geometry("1200x800")
        
        # Variables
        self.is_monitoring = False
        self.monitor_thread = None
        self.agent_colors = {}
        self.color_palette = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ]
        
        self.setup_gui()
        self.load_agents()
        
    def setup_gui(self):
        """Setup the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Multi-Agent Conversation Visualizer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Left panel - Agents
        agents_frame = ttk.LabelFrame(main_frame, text="Active Agents", padding="5")
        agents_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Agents listbox
        self.agents_listbox = tk.Listbox(agents_frame, height=15, width=25)
        self.agents_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Agent details
        agent_details_frame = ttk.Frame(agents_frame)
        agent_details_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(agent_details_frame, text="Agent Details:").pack(anchor=tk.W)
        self.agent_details_text = tk.Text(agent_details_frame, height=4, width=25, 
                                         font=('Arial', 9))
        self.agent_details_text.pack(fill=tk.X)
        
        # Middle panel - Conversation
        conversation_frame = ttk.LabelFrame(main_frame, text="Live Conversation", padding="5")
        conversation_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
        conversation_frame.columnconfigure(0, weight=1)
        conversation_frame.rowconfigure(0, weight=1)
        
        # Conversation display
        self.conversation_text = scrolledtext.ScrolledText(conversation_frame, 
                                                          wrap=tk.WORD, 
                                                          font=('Arial', 10))
        self.conversation_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Right panel - Statistics and Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls & Stats", padding="5")
        control_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # Statistics
        stats_frame = ttk.Frame(control_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(stats_frame, text="Statistics:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        self.stats_labels = {
            'conversations': ttk.Label(stats_frame, text="Conversations: 0"),
            'messages': ttk.Label(stats_frame, text="Messages: 0"),
            'agents': ttk.Label(stats_frame, text="Agents: 0"),
            'active': ttk.Label(stats_frame, text="Status: Stopped")
        }
        
        for label in self.stats_labels.values():
            label.pack(anchor=tk.W, pady=1)
        
        # API Configuration
        api_frame = ttk.Frame(control_frame)
        api_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(api_frame, text="API Configuration:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        ttk.Label(api_frame, text="Ollama API URL:").pack(anchor=tk.W)
        self.api_url_var = tk.StringVar(value="http://localhost:11434")
        api_entry = ttk.Entry(api_frame, textvariable=self.api_url_var)
        api_entry.pack(fill=tk.X, pady=2)
        
        ttk.Button(api_frame, text="Test Connection", 
                  command=self.test_api_connection).pack(fill=tk.X, pady=2)
        
        # Connection status
        self.connection_status = ttk.Label(api_frame, text="Status: Not tested", 
                                          foreground="gray")
        self.connection_status.pack(anchor=tk.W, pady=2)
        
        # Controls
        controls_frame = ttk.Frame(control_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(controls_frame, text="Controls:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        self.start_button = ttk.Button(controls_frame, text="Start Monitoring", 
                                      command=self.toggle_monitoring)
        self.start_button.pack(fill=tk.X, pady=2)
        
        ttk.Button(controls_frame, text="Clear Conversation", 
                  command=self.clear_conversation).pack(fill=tk.X, pady=2)
        
        ttk.Button(controls_frame, text="Refresh Agents", 
                  command=self.load_agents).pack(fill=tk.X, pady=2)
        
        ttk.Button(controls_frame, text="Export Conversation", 
                  command=self.export_conversation).pack(fill=tk.X, pady=2)
        
        ttk.Button(controls_frame, text="Generate Highlights", 
                  command=self.generate_highlights).pack(fill=tk.X, pady=2)
        
        # Conversation selector
        selector_frame = ttk.Frame(control_frame)
        selector_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(selector_frame, text="View Conversation:", font=('Arial', 11, 'bold')).pack(anchor=tk.W)
        
        self.conversation_var = tk.StringVar()
        self.conversation_combo = ttk.Combobox(selector_frame, textvariable=self.conversation_var,
                                             state="readonly")
        self.conversation_combo.pack(fill=tk.X, pady=2)
        self.conversation_combo.bind('<<ComboboxSelected>>', self.load_selected_conversation)
        
        ttk.Button(selector_frame, text="Refresh Conversations", 
                  command=self.load_conversations).pack(fill=tk.X, pady=2)
        
        # Bind events
        self.agents_listbox.bind('<<ListboxSelect>>', self.on_agent_select)
        
        # Configure text tags for colored agent messages
        self.setup_text_tags()
        
    def setup_text_tags(self):
        """Setup text tags for colored agent messages"""
        for i, color in enumerate(self.color_palette):
            tag_name = f"agent_color_{i}"
            self.conversation_text.tag_configure(tag_name, foreground=color, font=('Arial', 10, 'bold'))
    
    def load_agents(self):
        """Load agents from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, personality_traits, current_focus, model, conversation_style
                FROM agents ORDER BY name
            ''')
            
            agents = cursor.fetchall()
            conn.close()
            
            # Clear and populate agents listbox
            self.agents_listbox.delete(0, tk.END)
            self.agent_colors.clear()
            
            for i, agent in enumerate(agents):
                agent_id, name, traits, focus, model, style = agent
                self.agents_listbox.insert(tk.END, f"{name} ({model})")
                
                # Assign color to agent
                color_index = i % len(self.color_palette)
                self.agent_colors[agent_id] = color_index
            
            # Update stats
            self.stats_labels['agents'].config(text=f"Agents: {len(agents)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agents: {e}")
    
    def load_conversations(self):
        """Load conversation list"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT DISTINCT conversation_id, COUNT(*) as message_count,
                       MIN(timestamp) as start_time
                FROM messages 
                GROUP BY conversation_id 
                ORDER BY start_time DESC
            ''')
            
            conversations = cursor.fetchall()
            conn.close()
            
            # Update combo box
            conv_list = []
            for conv_id, msg_count, start_time in conversations:
                display_name = f"{conv_id[:8]}... ({msg_count} messages)"
                conv_list.append((display_name, conv_id))
            
            self.conversation_combo['values'] = [item[0] for item in conv_list]
            self.conversation_data = dict(conv_list)
            
            # Update stats
            self.stats_labels['conversations'].config(text=f"Conversations: {len(conversations)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conversations: {e}")
    
    def load_selected_conversation(self, event=None):
        """Load selected conversation from combo box"""
        selected = self.conversation_var.get()
        if selected and selected in self.conversation_data:
            conv_id = self.conversation_data[selected]
            self.load_conversation(conv_id)
    
    def load_conversation(self, conversation_id: str):
        """Load a specific conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.timestamp, m.agent_id, m.content, a.name
                FROM messages m
                LEFT JOIN agents a ON m.agent_id = a.id
                WHERE m.conversation_id = ?
                ORDER BY m.timestamp ASC
            ''', (conversation_id,))
            
            messages = cursor.fetchall()
            conn.close()
            
            # Clear and display conversation
            self.conversation_text.delete(1.0, tk.END)
            
            for timestamp, agent_id, content, agent_name in messages:
                self.add_message_to_display(agent_id, agent_name or "Unknown", content, timestamp)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conversation: {e}")
    
    def on_agent_select(self, event):
        """Handle agent selection"""
        selection = self.agents_listbox.curselection()
        if not selection:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get agent details (index corresponds to database order)
            cursor.execute('''
                SELECT name, personality_traits, current_focus, model, conversation_style
                FROM agents ORDER BY name LIMIT 1 OFFSET ?
            ''', (selection[0],))
            
            agent = cursor.fetchone()
            conn.close()
            
            if agent:
                name, traits, focus, model, style = agent
                traits_list = json.loads(traits) if traits else []
                
                details = f"Name: {name}\n"
                details += f"Model: {model}\n"
                details += f"Focus: {focus}\n"
                details += f"Style: {style}\n"
                details += f"Traits: {', '.join(traits_list)}"
                
                self.agent_details_text.delete(1.0, tk.END)
                self.agent_details_text.insert(1.0, details)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load agent details: {e}")
    
    def toggle_monitoring(self):
        """Toggle real-time monitoring"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        self.is_monitoring = True
        self.start_button.config(text="Stop Monitoring")
        self.stats_labels['active'].config(text="Status: Monitoring")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        self.start_button.config(text="Start Monitoring")
        self.stats_labels['active'].config(text="Status: Stopped")
    
    def monitor_loop(self):
        """Monitor database for new messages"""
        last_check = datetime.now()
        
        while self.is_monitoring:
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get messages since last check
                cursor.execute('''
                    SELECT m.timestamp, m.agent_id, m.content, a.name
                    FROM messages m
                    LEFT JOIN agents a ON m.agent_id = a.id
                    WHERE m.timestamp > ?
                    ORDER BY m.timestamp ASC
                ''', (last_check.isoformat(),))
                
                new_messages = cursor.fetchall()
                
                # Update total message count
                cursor.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]
                
                conn.close()
                
                # Update GUI in main thread
                if new_messages:
                    self.root.after(0, self.update_gui_with_messages, new_messages)
                
                self.root.after(0, self.update_message_count, total_messages)
                
                last_check = datetime.now()
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(5)
    
    def update_gui_with_messages(self, messages):
        """Update GUI with new messages (called from main thread)"""
        for timestamp, agent_id, content, agent_name in messages:
            self.add_message_to_display(agent_id, agent_name or "Unknown", content, timestamp)
    
    def update_message_count(self, count):
        """Update message count (called from main thread)"""
        self.stats_labels['messages'].config(text=f"Messages: {count}")
    
    def add_message_to_display(self, agent_id: str, agent_name: str, content: str, timestamp: str):
        """Add a message to the conversation display"""
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp
        
        # Get agent color
        color_index = self.agent_colors.get(agent_id, 0)
        tag_name = f"agent_color_{color_index}"
        
        # Add message to display
        self.conversation_text.insert(tk.END, f"[{time_str}] ")
        self.conversation_text.insert(tk.END, f"{agent_name}:\n", tag_name)
        self.conversation_text.insert(tk.END, f"  {content}\n\n")
        
        # Auto-scroll to bottom
        self.conversation_text.see(tk.END)
    
    def clear_conversation(self):
        """Clear the conversation display"""
        self.conversation_text.delete(1.0, tk.END)
    
    def test_api_connection(self):
        """Test connection to Ollama API"""
        api_url = self.api_url_var.get().strip()
        if not api_url:
            messagebox.showwarning("Warning", "Please enter an API URL")
            return
        
        try:
            # Test connection with a simple request
            response = requests.get(f"{api_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_count = len(models)
                self.connection_status.config(text=f"Status: Connected ({model_count} models)", 
                                            foreground="green")
                messagebox.showinfo("Success", f"Connected successfully!\nFound {model_count} models.")
            else:
                self.connection_status.config(text="Status: Connection failed", 
                                            foreground="red")
                messagebox.showerror("Error", f"Connection failed with status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.connection_status.config(text="Status: Connection failed", 
                                        foreground="red")
            messagebox.showerror("Error", f"Connection failed: {str(e)}")
    
    def generate_highlights(self):
        """Generate AI highlights of the current conversation"""
        content = self.conversation_text.get(1.0, tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "No conversation to analyze")
            return
        
        api_url = self.api_url_var.get().strip()
        if not api_url:
            messagebox.showwarning("Warning", "Please configure API URL first")
            return
        
        # Show progress dialog
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Generating Highlights")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text="Analyzing conversation...").pack(pady=20)
        progress_bar = ttk.Progressbar(progress_window, mode='indeterminate')
        progress_bar.pack(pady=10)
        progress_bar.start()
        
        # Generate highlights in background thread
        def generate_in_background():
            try:
                highlights = self._generate_conversation_highlights(content, api_url)
                self.root.after(0, self._show_highlights_window, highlights, progress_window)
            except Exception as e:
                self.root.after(0, self._show_error_and_close, str(e), progress_window)
        
        threading.Thread(target=generate_in_background, daemon=True).start()
    
    def _generate_conversation_highlights(self, conversation_text: str, api_url: str) -> str:
        """Generate highlights using the AI API"""
        # Create a prompt for generating highlights
        prompt = f"""Analyze this conversation between AI agents and generate key highlights:

CONVERSATION:
{conversation_text}

Please provide:
1. Key insights and discoveries
2. Important connections made
3. Novel ideas or perspectives
4. Breakthrough moments
5. Interesting patterns or themes

Format as a clear, structured summary:"""
        
        try:
            # LM Studio uses OpenAI-compatible API format
            response = requests.post(
                f"{api_url}/chat/completions",
                json={
                    "model": "gemma2:2b",  # Default model, could make this configurable
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', 'No highlights generated').strip()
            else:
                return f"API Error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Connection Error: {str(e)}"
    
    def _show_highlights_window(self, highlights: str, progress_window: tk.Toplevel):
        """Show highlights in a new window"""
        progress_window.destroy()
        
        # Create highlights window
        highlights_window = tk.Toplevel(self.root)
        highlights_window.title("🌟 AI-Generated Conversation Highlights")
        highlights_window.geometry("600x500")
        highlights_window.transient(self.root)
        
        # Header
        header_frame = ttk.Frame(highlights_window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text="AI-Generated Highlights", 
                 font=('Arial', 14, 'bold')).pack(anchor=tk.W)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ttk.Label(header_frame, text=f"Generated: {timestamp}", 
                 font=('Arial', 9), foreground="gray").pack(anchor=tk.W)
        
        # Highlights text
        text_frame = ttk.Frame(highlights_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        highlights_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                   font=('Arial', 10))
        highlights_text.pack(fill=tk.BOTH, expand=True)
        highlights_text.insert(1.0, highlights)
        highlights_text.config(state=tk.DISABLED)  # Make read-only
        
        # Buttons
        button_frame = ttk.Frame(highlights_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def save_highlights():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"highlights_{timestamp}.txt"
            try:
                with open(filename, 'w') as f:
                    f.write(f"AI-Generated Conversation Highlights\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(highlights)
                messagebox.showinfo("Saved", f"Highlights saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
        
        ttk.Button(button_frame, text="Save Highlights", 
                  command=save_highlights).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", 
                  command=highlights_window.destroy).pack(side=tk.RIGHT)
    
    def _show_error_and_close(self, error_msg: str, progress_window: tk.Toplevel):
        """Show error and close progress window"""
        progress_window.destroy()
        messagebox.showerror("Error", f"Failed to generate highlights: {error_msg}")
    
    def export_conversation(self):
        """Export current conversation to file"""
        content = self.conversation_text.get(1.0, tk.END)
        if content.strip():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_export_{timestamp}.txt"
            
            try:
                with open(filename, 'w') as f:
                    f.write(content)
                messagebox.showinfo("Export", f"Conversation exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
        else:
            messagebox.showwarning("Warning", "No conversation to export")
    
    def run(self):
        """Run the GUI application"""
        # Load initial data
        self.load_conversations()
        
        # Start the GUI
        self.root.mainloop()


def main():
    """Main entry point for GUI visualizer"""
    app = AgentConversationGUI()
    app.run()


if __name__ == "__main__":
    main()
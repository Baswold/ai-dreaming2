#!/usr/bin/env python3
"""
Web-based monitoring interface for agent conversations
Real-time visualization of multi-agent thinking
"""

import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
from pathlib import Path


app = Flask(__name__)


class ConversationMonitor:
    """Real-time monitoring for agent conversations"""
    
    def __init__(self, db_path: str = "multi_agent_memory.db"):
        self.db_path = db_path
        self.active_conversations = {}
        self.recent_messages = []
        self.max_recent = 100
    
    def get_agents(self):
        """Get all agents from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, name, personality_traits, current_focus, model, conversation_style
                FROM agents
                ORDER BY name
            ''')
            
            agents = []
            for row in cursor.fetchall():
                agents.append({
                    'id': row[0],
                    'name': row[1],
                    'personality_traits': json.loads(row[2]) if row[2] else [],
                    'current_focus': row[3],
                    'model': row[4],
                    'conversation_style': row[5]
                })
            
            conn.close()
            return agents
            
        except Exception as e:
            print(f"Error getting agents: {e}")
            return []
    
    def get_recent_messages(self, limit: int = 50):
        """Get recent messages across all conversations"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.id, m.timestamp, m.agent_id, m.content, m.conversation_id,
                       a.name as agent_name, a.personality_traits
                FROM messages m
                LEFT JOIN agents a ON m.agent_id = a.id
                ORDER BY m.timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'agent_id': row[2],
                    'content': row[3],
                    'conversation_id': row[4],
                    'agent_name': row[5] or 'Unknown',
                    'personality_traits': json.loads(row[6]) if row[6] else []
                })
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Error getting messages: {e}")
            return []
    
    def get_conversation_stats(self):
        """Get conversation statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total conversations
            cursor.execute('SELECT COUNT(*) FROM (SELECT DISTINCT conversation_id FROM messages)')
            total_conversations = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute('SELECT COUNT(*) FROM messages')
            total_messages = cursor.fetchone()[0]
            
            # Messages today
            today = datetime.now().strftime('%Y-%m-%d')
            cursor.execute('SELECT COUNT(*) FROM messages WHERE timestamp LIKE ?', (f'{today}%',))
            messages_today = cursor.fetchone()[0]
            
            # Active agents
            cursor.execute('SELECT COUNT(*) FROM agents')
            total_agents = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_conversations': total_conversations,
                'total_messages': total_messages,
                'messages_today': messages_today,
                'total_agents': total_agents
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def get_conversation_details(self, conversation_id: str):
        """Get details for a specific conversation"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT m.id, m.timestamp, m.agent_id, m.content,
                       a.name as agent_name, a.personality_traits
                FROM messages m
                LEFT JOIN agents a ON m.agent_id = a.id
                WHERE m.conversation_id = ?
                ORDER BY m.timestamp ASC
            ''', (conversation_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'timestamp': row[1],
                    'agent_id': row[2],
                    'content': row[3],
                    'agent_name': row[4] or 'Unknown',
                    'personality_traits': json.loads(row[5]) if row[5] else []
                })
            
            conn.close()
            return messages
            
        except Exception as e:
            print(f"Error getting conversation details: {e}")
            return []


monitor = ConversationMonitor()


@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/agents')
def api_agents():
    """Get all agents"""
    agents = monitor.get_agents()
    return jsonify(agents)


@app.route('/api/messages/recent')
def api_recent_messages():
    """Get recent messages"""
    limit = request.args.get('limit', 50, type=int)
    messages = monitor.get_recent_messages(limit)
    return jsonify(messages)


@app.route('/api/stats')
def api_stats():
    """Get conversation statistics"""
    stats = monitor.get_conversation_stats()
    return jsonify(stats)


@app.route('/api/conversation/<conversation_id>')
def api_conversation(conversation_id):
    """Get specific conversation"""
    messages = monitor.get_conversation_details(conversation_id)
    return jsonify(messages)


# Create templates directory and files
def create_templates():
    """Create HTML templates for the web interface"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Agent Conversation Monitor</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .agents-section, .messages-section {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .agent-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background: #f9f9f9;
        }
        .agent-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        .agent-traits {
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin: 2px;
            display: inline-block;
        }
        .message {
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 10px 0;
            background: white;
            border-radius: 0 8px 8px 0;
        }
        .message-header {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }
        .message-content {
            color: #333;
            line-height: 1.5;
        }
        .timestamp {
            color: #666;
            font-size: 0.9em;
            margin-top: 8px;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #5a6fd8;
        }
        .auto-refresh {
            color: #666;
            font-size: 0.9em;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Multi-Agent Conversation Monitor</h1>
        <p>Real-time monitoring of autonomous agent conversations</p>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number" id="total-conversations">-</div>
            <div>Total Conversations</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="total-messages">-</div>
            <div>Total Messages</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="messages-today">-</div>
            <div>Messages Today</div>
        </div>
        <div class="stat-card">
            <div class="stat-number" id="total-agents">-</div>
            <div>Active Agents</div>
        </div>
    </div>

    <div class="agents-section">
        <h2>Active Agents</h2>
        <div id="agents-container">
            Loading agents...
        </div>
    </div>

    <div class="messages-section">
        <h2>Recent Conversations</h2>
        <button class="refresh-btn" onclick="loadMessages()">Refresh Messages</button>
        <span class="auto-refresh">Auto-refreshing every 5 seconds</span>
        <div id="messages-container">
            Loading messages...
        </div>
    </div>

    <script>
        function loadStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-conversations').textContent = data.total_conversations || 0;
                    document.getElementById('total-messages').textContent = data.total_messages || 0;
                    document.getElementById('messages-today').textContent = data.messages_today || 0;
                    document.getElementById('total-agents').textContent = data.total_agents || 0;
                })
                .catch(error => console.error('Error loading stats:', error));
        }

        function loadAgents() {
            fetch('/api/agents')
                .then(response => response.json())
                .then(agents => {
                    const container = document.getElementById('agents-container');
                    if (agents.length === 0) {
                        container.innerHTML = '<p>No agents found. Start the multi-agent system to see agents here.</p>';
                        return;
                    }
                    
                    container.innerHTML = agents.map(agent => `
                        <div class="agent-card">
                            <div class="agent-name">${agent.name} (${agent.model})</div>
                            <div>Focus: ${agent.current_focus}</div>
                            <div>Style: ${agent.conversation_style}</div>
                            <div>
                                ${agent.personality_traits.map(trait => 
                                    `<span class="agent-traits">${trait}</span>`
                                ).join('')}
                            </div>
                        </div>
                    `).join('');
                })
                .catch(error => console.error('Error loading agents:', error));
        }

        function loadMessages() {
            fetch('/api/messages/recent?limit=20')
                .then(response => response.json())
                .then(messages => {
                    const container = document.getElementById('messages-container');
                    if (messages.length === 0) {
                        container.innerHTML = '<p>No messages yet. Start a conversation to see messages here.</p>';
                        return;
                    }
                    
                    container.innerHTML = messages.map(message => `
                        <div class="message">
                            <div class="message-header">
                                ${message.agent_name} 
                                <span style="font-weight: normal; color: #666;">
                                    (${message.conversation_id.substring(0, 8)}...)
                                </span>
                            </div>
                            <div class="message-content">${message.content}</div>
                            <div class="timestamp">${new Date(message.timestamp).toLocaleString()}</div>
                        </div>
                    `).join('');
                })
                .catch(error => console.error('Error loading messages:', error));
        }

        // Load data on page load
        document.addEventListener('DOMContentLoaded', function() {
            loadStats();
            loadAgents();
            loadMessages();
            
            // Auto-refresh every 5 seconds
            setInterval(() => {
                loadStats();
                loadMessages();
            }, 5000);
            
            // Refresh agents every 30 seconds
            setInterval(loadAgents, 30000);
        });
    </script>
</body>
</html>'''
    
    with open(templates_dir / "dashboard.html", "w") as f:
        f.write(dashboard_html)


def main():
    """Run the web monitoring interface"""
    create_templates()
    
    print("🌐 Starting web monitoring interface...")
    print("📊 Dashboard will be available at: http://localhost:8080")
    
    app.run(host='0.0.0.0', port=8080, debug=False)


if __name__ == "__main__":
    main()
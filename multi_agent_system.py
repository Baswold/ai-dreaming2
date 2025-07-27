#!/usr/bin/env python3
"""
Multi-Agent Conversation System
Creates autonomous agents that engage in conversations without system prompts
"""

import json
import time
import random
import sqlite3
import threading
import queue
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

import requests
from dataclasses import dataclass, asdict


@dataclass
class AgentMessage:
    """Represents a message in agent conversation"""
    id: str
    timestamp: datetime
    agent_id: str
    content: str
    response_to: Optional[str] = None
    conversation_id: str = ""
    interest_score: float = 0.0


@dataclass
class Agent:
    """Represents an autonomous agent"""
    id: str
    name: str
    personality_traits: List[str]
    current_focus: str
    model: str
    conversation_style: str
    memory_buffer: List[AgentMessage] = None
    
    def __post_init__(self):
        if self.memory_buffer is None:
            self.memory_buffer = []


class AgentPersonalityGenerator:
    """Generates diverse personalities for agents"""
    
    def __init__(self):
        self.personality_traits = [
            "curious", "analytical", "creative", "methodical", "intuitive",
            "skeptical", "optimistic", "philosophical", "practical", "imaginative",
            "logical", "empathetic", "bold", "cautious", "innovative"
        ]
        
        self.conversation_styles = [
            "questioning", "storytelling", "technical", "metaphorical", "direct",
            "exploratory", "building_on_ideas", "challenging", "synthesizing", "divergent"
        ]
        
        self.focus_areas = [
            "patterns", "connections", "contradictions", "possibilities", "fundamentals",
            "applications", "implications", "origins", "futures", "relationships"
        ]
    
    def generate_agent(self, agent_id: str, model: str) -> Agent:
        """Generate a unique agent personality"""
        traits = random.sample(self.personality_traits, random.randint(2, 4))
        style = random.choice(self.conversation_styles)
        focus = random.choice(self.focus_areas)
        
        # Create memorable names based on traits
        name_prefixes = {
            "curious": "Explorer", "analytical": "Analyzer", "creative": "Dreamer",
            "methodical": "Builder", "intuitive": "Seer", "skeptical": "Questioner",
            "optimistic": "Visionary", "philosophical": "Thinker", "practical": "Maker",
            "imaginative": "Weaver", "logical": "Reasoner", "empathetic": "Connector",
            "bold": "Pioneer", "cautious": "Guardian", "innovative": "Inventor"
        }
        
        primary_trait = traits[0]
        name = f"{name_prefixes.get(primary_trait, 'Agent')}-{agent_id[-3:]}"
        
        return Agent(
            id=agent_id,
            name=name,
            personality_traits=traits,
            current_focus=focus,
            model=model,
            conversation_style=style
        )


class ConversationEngine:
    """Manages multi-agent conversations"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.agents: Dict[str, Agent] = {}
        self.conversations: Dict[str, List[AgentMessage]] = {}
        self.message_queue = queue.Queue()
        self.is_running = False
        
    def add_agent(self, agent: Agent):
        """Add an agent to the system"""
        self.agents[agent.id] = agent
        logging.info(f"Added agent: {agent.name} ({agent.id})")
    
    def start_conversation(self, conversation_id: str, initial_topic: str = None) -> str:
        """Start a new conversation between agents"""
        if conversation_id in self.conversations:
            return conversation_id
            
        self.conversations[conversation_id] = []
        
        # Generate initial message from random agent or seed topic
        if initial_topic:
            seed_message = initial_topic
        else:
            seed_message = self._generate_conversation_seed()
        
        # Select first agent to speak
        first_agent = random.choice(list(self.agents.values()))
        
        initial_message = AgentMessage(
            id=f"msg_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            agent_id=first_agent.id,
            content=seed_message,
            conversation_id=conversation_id
        )
        
        self.conversations[conversation_id].append(initial_message)
        self.message_queue.put(initial_message)
        
        logging.info(f"Started conversation {conversation_id} with {first_agent.name}")
        return conversation_id
    
    def _generate_conversation_seed(self) -> str:
        """Generate an initial conversation topic"""
        seeds = [
            "I've been thinking about the nature of time...",
            "What if consciousness is more like water than we think?",
            "There's something fascinating about how patterns emerge everywhere.",
            "I wonder about the connection between music and mathematics.",
            "The way plants grow reminds me of how ideas spread.",
            "Have you noticed how cities breathe like living organisms?",
            "The space between thoughts might be where creativity lives.",
            "I'm curious about what makes something beautiful versus useful.",
            "The relationship between order and chaos keeps puzzling me.",
            "Sometimes I think language shapes reality more than we realize."
        ]
        return random.choice(seeds)
    
    def generate_response(self, agent: Agent, conversation_history: List[AgentMessage]) -> str:
        """Generate agent response based on personality and conversation history"""
        # Build context from recent conversation
        recent_messages = conversation_history[-5:]  # Last 5 messages
        context = ""
        
        for msg in recent_messages:
            speaker = self.agents.get(msg.agent_id, Agent("unknown", "Unknown", [], "", "")).name
            context += f"{speaker}: {msg.content}\n"
        
        # Build personality-driven prompt
        prompt = self._build_agent_prompt(agent, context)
        
        try:
            # LM Studio uses OpenAI-compatible API format
            response = requests.post(
                f"{self.ollama_url}/chat/completions",
                json={
                    "model": agent.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": random.uniform(0.7, 1.1),
                    "top_p": 0.9,
                    "max_tokens": 150,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            else:
                logging.error(f"API error for {agent.name}: {response.status_code}")
                return self._fallback_response(agent)
                
        except Exception as e:
            logging.error(f"Error generating response for {agent.name}: {e}")
            return self._fallback_response(agent)
    
    def _build_agent_prompt(self, agent: Agent, context: str) -> str:
        """Build personality-driven prompt for agent"""
        # No system prompt - let personality emerge from context
        personality_desc = f"Agent with traits: {', '.join(agent.personality_traits)}"
        style_desc = f"Communication style: {agent.conversation_style}"
        focus_desc = f"Current focus: {agent.current_focus}"
        
        prompt = f"""Recent conversation:
{context}

{personality_desc}
{style_desc}
{focus_desc}

Response (continue the conversation naturally):"""
        
        return prompt
    
    def _fallback_response(self, agent: Agent) -> str:
        """Generate fallback response when API fails"""
        fallbacks = [
            "That's an interesting perspective...",
            "I'm still processing that thought.",
            "Something about this reminds me of...",
            "Let me think about this differently.",
            "What if we considered...",
            "That opens up new questions for me."
        ]
        return random.choice(fallbacks)
    
    def process_conversation(self, conversation_id: str, max_exchanges: int = 20):
        """Process conversation between agents"""
        if conversation_id not in self.conversations:
            logging.error(f"Conversation {conversation_id} not found")
            return
        
        conversation = self.conversations[conversation_id]
        exchanges = 0
        
        while exchanges < max_exchanges:
            try:
                # Select next agent to respond (not the last speaker)
                last_speaker = conversation[-1].agent_id if conversation else None
                available_agents = [a for a in self.agents.values() if a.id != last_speaker]
                
                if not available_agents:
                    break
                    
                next_agent = random.choice(available_agents)
                
                # Generate response
                response_content = self.generate_response(next_agent, conversation)
                
                if response_content:
                    response_msg = AgentMessage(
                        id=f"msg_{int(time.time() * 1000)}_{exchanges}",
                        timestamp=datetime.now(),
                        agent_id=next_agent.id,
                        content=response_content,
                        response_to=conversation[-1].id if conversation else None,
                        conversation_id=conversation_id
                    )
                    
                    conversation.append(response_msg)
                    self.message_queue.put(response_msg)
                    
                    # Update agent memory
                    next_agent.memory_buffer.append(response_msg)
                    if len(next_agent.memory_buffer) > 10:
                        next_agent.memory_buffer.pop(0)
                    
                    exchanges += 1
                    
                    # Wait between responses
                    time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logging.error(f"Error in conversation processing: {e}")
                break
        
        logging.info(f"Conversation {conversation_id} completed with {exchanges} exchanges")


class MultiAgentMemory:
    """Memory system for multi-agent conversations"""
    
    def __init__(self, db_path: str = "multi_agent_memory.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database for agent conversations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                personality_traits TEXT,
                current_focus TEXT,
                model TEXT,
                conversation_style TEXT,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                agent_id TEXT,
                content TEXT,
                response_to TEXT,
                conversation_id TEXT,
                interest_score REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                started_at TEXT,
                ended_at TEXT,
                participant_count INTEGER,
                message_count INTEGER,
                topic TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_agent(self, agent: Agent):
        """Save agent to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO agents 
            (id, name, personality_traits, current_focus, model, conversation_style, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            agent.id,
            agent.name,
            json.dumps(agent.personality_traits),
            agent.current_focus,
            agent.model,
            agent.conversation_style,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def save_message(self, message: AgentMessage):
        """Save message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO messages 
            (id, timestamp, agent_id, content, response_to, conversation_id, interest_score)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            message.id,
            message.timestamp.isoformat(),
            message.agent_id,
            message.content,
            message.response_to,
            message.conversation_id,
            message.interest_score
        ))
        
        conn.commit()
        conn.close()


class MultiAgentSystem:
    """Main orchestrator for multi-agent conversations"""
    
    def __init__(self, config_path: str = "multi_agent_config.json"):
        self.config = self._load_config(config_path)
        self.personality_generator = AgentPersonalityGenerator()
        self.conversation_engine = ConversationEngine(
            ollama_url=self.config.get('ollama_url', 'http://localhost:11434')
        )
        self.memory = MultiAgentMemory(self.config.get('db_path', 'multi_agent_memory.db'))
        self.active_conversations = {}
        
        # Initialize agents
        self._create_agents()
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration"""
        default_config = {
            "models": ["gemma2:2b", "qwen2.5:1.5b", "phi3:mini"],
            "agent_count": 3,
            "ollama_url": "http://localhost:11434",
            "db_path": "multi_agent_memory.db",
            "conversation_duration": 300,  # seconds
            "max_exchanges_per_conversation": 20
        }
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default multi-agent configuration: {config_path}")
        
        return default_config
    
    def _create_agents(self):
        """Create initial set of agents"""
        models = self.config.get('models', ['gemma2:2b'])
        agent_count = self.config.get('agent_count', 3)
        
        for i in range(agent_count):
            agent_id = f"agent_{int(time.time() * 1000)}_{i}"
            model = models[i % len(models)]
            
            agent = self.personality_generator.generate_agent(agent_id, model)
            self.conversation_engine.add_agent(agent)
            self.memory.save_agent(agent)
            
            print(f"Created agent: {agent.name} - {', '.join(agent.personality_traits)}")
    
    def start_conversation_session(self, topic: str = None) -> str:
        """Start a new conversation session"""
        conversation_id = f"conv_{int(time.time() * 1000)}"
        
        # Start conversation
        self.conversation_engine.start_conversation(conversation_id, topic)
        
        # Process conversation in background thread
        conversation_thread = threading.Thread(
            target=self.conversation_engine.process_conversation,
            args=(conversation_id, self.config.get('max_exchanges_per_conversation', 20))
        )
        conversation_thread.daemon = True
        conversation_thread.start()
        
        self.active_conversations[conversation_id] = conversation_thread
        
        print(f"Started conversation session: {conversation_id}")
        return conversation_id
    
    def monitor_conversations(self):
        """Monitor and display ongoing conversations"""
        print("🤖 Multi-Agent Conversation System")
        print("=" * 50)
        
        try:
            while True:
                try:
                    # Get message from queue with timeout
                    message = self.conversation_engine.message_queue.get(timeout=1)
                    
                    # Save to memory
                    self.memory.save_message(message)
                    
                    # Display message
                    agent = self.conversation_engine.agents.get(message.agent_id)
                    agent_name = agent.name if agent else "Unknown"
                    timestamp = message.timestamp.strftime("%H:%M:%S")
                    
                    print(f"\n[{timestamp}] {agent_name}:")
                    print(f"  {message.content}")
                    print("-" * 40)
                    
                except queue.Empty:
                    # Check if any conversations are still active
                    active = any(thread.is_alive() for thread in self.active_conversations.values())
                    if not active and not self.active_conversations:
                        break
                    continue
                    
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")


def main():
    """Main entry point for multi-agent system"""
    print("🤖 Multi-Agent Thinking System")
    print("=" * 40)
    
    system = MultiAgentSystem()
    
    while True:
        print("\nCommands:")
        print("1. start - Start new conversation")
        print("2. topic - Start conversation with topic")
        print("3. monitor - Monitor active conversations")
        print("4. quit - Exit")
        
        choice = input("\nEnter command: ").strip().lower()
        
        if choice in ['1', 'start']:
            conversation_id = system.start_conversation_session()
            system.monitor_conversations()
            
        elif choice in ['2', 'topic']:
            topic = input("Enter conversation topic: ").strip()
            conversation_id = system.start_conversation_session(topic)
            system.monitor_conversations()
            
        elif choice in ['3', 'monitor']:
            system.monitor_conversations()
            
        elif choice in ['4', 'quit', 'exit']:
            print("👋 Goodbye!")
            break
            
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
DreamingAI - A continuous reasoning loop system for local language models

This system runs autonomous reasoning loops without requiring user prompts,
allowing AI models to explore ideas, make connections, and discover insights
through pure thought processes.
"""

import json
import time
import random
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

import requests
from dataclasses import dataclass, asdict


@dataclass
class Thought:
    """Represents a single thought in the reasoning chain"""
    id: str
    timestamp: datetime
    content: str
    thought_type: str  # seed, reasoning, branch, insight, gold_strike
    parent_id: Optional[str] = None
    interest_score: float = 0.0
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class ThoughtSeeder:
    """Generates initial topics and seeds for autonomous reasoning"""
    
    def __init__(self):
        self.abstract_concepts = [
            "consciousness", "infinity", "emergence", "patterns", "symmetry",
            "chaos", "order", "connection", "transformation", "paradox",
            "beauty", "truth", "existence", "meaning", "purpose", "time",
            "space", "energy", "information", "complexity", "simplicity"
        ]
        
        self.concrete_concepts = [
            "ocean", "mountain", "tree", "bird", "crystal", "river", "star",
            "flower", "stone", "wind", "fire", "ice", "light", "shadow",
            "music", "dance", "color", "texture", "sound", "silence"
        ]
        
        self.abstract_questions = [
            "What if time moved backwards?",
            "How do patterns emerge from chaos?",
            "What connects all living things?",
            "Why do we find certain things beautiful?",
            "What is the nature of consciousness?",
            "How does complexity arise from simplicity?",
            "What would a perfect system look like?",
            "How do ideas spread and evolve?",
            "What makes something meaningful?",
            "How do we know what we know?"
        ]
    
    def generate_seed(self) -> str:
        """Generate a random seed for thinking"""
        seed_type = random.choice(['combination', 'abstract_question', 'timestamp_based'])
        
        if seed_type == 'combination':
            concept1 = random.choice(self.abstract_concepts + self.concrete_concepts)
            concept2 = random.choice(self.abstract_concepts + self.concrete_concepts)
            while concept2 == concept1:
                concept2 = random.choice(self.abstract_concepts + self.concrete_concepts)
            return f"{concept1} + {concept2}"
        
        elif seed_type == 'abstract_question':
            return random.choice(self.abstract_questions)
        
        else:  # timestamp_based
            current_time = datetime.now()
            time_prompts = [
                f"It's {current_time.strftime('%H:%M')} on a {current_time.strftime('%A')}. What might be happening right now?",
                f"In this moment at {current_time.strftime('%H:%M')}, what thoughts arise?",
                f"The time is {current_time.strftime('%H:%M:%S')}. What does this precise moment contain?"
            ]
            return random.choice(time_prompts)


class ReasoningEngine:
    """Handles different modes of reasoning and thought generation"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma2:2b"):
        self.ollama_url = ollama_url
        self.model = model
        self.reasoning_modes = [
            'free_association',
            'logical_deduction',
            'creative_what_if',
            'pattern_recognition',
            'analogical_reasoning'
        ]
    
    def generate_thought(self, context: List[Thought], mode: str = None) -> str:
        """Generate a new thought based on context and reasoning mode"""
        if mode is None:
            mode = random.choice(self.reasoning_modes)
        
        # Build context string from recent thoughts
        context_str = ""
        if context:
            recent_thoughts = context[-5:]  # Last 5 thoughts for context
            context_str = "\n".join([f"[{t.thought_type.upper()}] {t.content}" for t in recent_thoughts])
        
        prompt = self._build_prompt(context_str, mode)
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": random.uniform(0.7, 1.2),  # Creativity variance
                        "top_p": 0.9,
                        "max_tokens": 200
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logging.error(f"Ollama API error: {response.status_code}")
                return "I notice something interesting about the nature of thought itself..."
                
        except Exception as e:
            logging.error(f"Error generating thought: {e}")
            return "In this moment of silence, new possibilities emerge..."
    
    def _build_prompt(self, context: str, mode: str) -> str:
        """Build appropriate prompt based on reasoning mode"""
        base_context = f"Previous thoughts:\n{context}\n\n" if context else ""
        
        mode_prompts = {
            'free_association': f"{base_context}Let your mind wander freely. What comes to mind next?",
            
            'logical_deduction': f"{base_context}Following logical steps, what conclusion emerges?",
            
            'creative_what_if': f"{base_context}What if we imagined something completely different? What if...",
            
            'pattern_recognition': f"{base_context}Looking at these ideas, what patterns or connections do you notice?",
            
            'analogical_reasoning': f"{base_context}How might this be similar to something else entirely? What analogy comes to mind?"
        }
        
        return mode_prompts.get(mode, f"{base_context}What thought arises naturally?")


class InterestDetector:
    """Identifies potentially interesting or valuable thoughts"""
    
    def __init__(self):
        self.interest_keywords = [
            'connection', 'pattern', 'similar', 'like', 'reminds me',
            'what if', 'perhaps', 'maybe', 'could be', 'might',
            'interesting', 'fascinating', 'beautiful', 'elegant',
            'paradox', 'contradiction', 'unexpected', 'surprising',
            'discovery', 'insight', 'realization', 'understanding'
        ]
        
        self.gold_strike_indicators = [
            'breakthrough', 'eureka', 'suddenly clear', 'now I see',
            'this explains', 'the key is', 'fundamental', 'profound',
            'revolutionary', 'paradigm', 'transforms everything'
        ]
    
    def calculate_interest_score(self, thought: str) -> float:
        """Calculate how interesting/valuable a thought might be"""
        score = 0.0
        thought_lower = thought.lower()
        
        # Basic interest keywords
        for keyword in self.interest_keywords:
            if keyword in thought_lower:
                score += 0.1
        
        # Gold strike indicators (higher value)
        for indicator in self.gold_strike_indicators:
            if indicator in thought_lower:
                score += 0.5
        
        # Length and complexity bonus
        if len(thought) > 100:
            score += 0.1
        
        # Question marks indicate curiosity
        score += thought.count('?') * 0.05
        
        # Exclamation marks indicate excitement/discovery
        score += thought.count('!') * 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def is_gold_strike(self, thought: str, score: float) -> bool:
        """Determine if this thought represents a significant discovery"""
        return score > 0.6 or any(indicator in thought.lower() for indicator in self.gold_strike_indicators)


class MemorySystem:
    """Manages short-term and long-term memory for thoughts"""
    
    def __init__(self, db_path: str = "dreaming_memory.db"):
        self.db_path = db_path
        self.short_term_memory: List[Thought] = []
        self.max_short_term = 20
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for long-term memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thoughts (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                content TEXT,
                thought_type TEXT,
                parent_id TEXT,
                interest_score REAL,
                tags TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS golden_thoughts (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                content TEXT,
                interest_score REAL,
                discovery_context TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_thought(self, thought: Thought):
        """Add thought to both short-term and long-term memory"""
        # Add to short-term memory
        self.short_term_memory.append(thought)
        
        # Maintain short-term memory size
        if len(self.short_term_memory) > self.max_short_term:
            self.short_term_memory.pop(0)
        
        # Store in long-term database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO thoughts 
            (id, timestamp, content, thought_type, parent_id, interest_score, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            thought.id,
            thought.timestamp.isoformat(),
            thought.content,
            thought.thought_type,
            thought.parent_id,
            thought.interest_score,
            json.dumps(thought.tags)
        ))
        
        conn.commit()
        conn.close()
    
    def add_golden_thought(self, thought: Thought, context: str = ""):
        """Store a particularly interesting thought in the golden collection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO golden_thoughts 
            (id, timestamp, content, interest_score, discovery_context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            thought.id,
            thought.timestamp.isoformat(),
            thought.content,
            thought.interest_score,
            context
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_thoughts(self, limit: int = 10) -> List[Thought]:
        """Get recent thoughts from short-term memory"""
        return self.short_term_memory[-limit:]
    
    def get_golden_thoughts(self) -> List[Dict]:
        """Retrieve all golden thoughts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, timestamp, content, interest_score, discovery_context
            FROM golden_thoughts
            ORDER BY interest_score DESC, timestamp DESC
        ''')
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'interest_score': row[3],
                'discovery_context': row[4]
            })
        
        conn.close()
        return results


class OutputManager:
    """Manages display and saving of thoughts and discoveries"""
    
    def __init__(self, output_dir: str = "dream_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'dreaming.log'),
                logging.StreamHandler()
            ]
        )
    
    def display_thought(self, thought: Thought):
        """Display a thought to console with formatting"""
        timestamp = thought.timestamp.strftime("%H:%M:%S")
        type_display = thought.thought_type.upper().replace('_', ' ')
        
        if thought.thought_type == 'gold_strike':
            print(f"\n🌟 [{timestamp}] {type_display} (Score: {thought.interest_score:.2f})")
            print(f"✨ {thought.content}")
            print("=" * 60)
        elif thought.interest_score > 0.4:
            print(f"\n💡 [{timestamp}] {type_display} (Score: {thought.interest_score:.2f})")
            print(f"   {thought.content}")
        else:
            print(f"\n💭 [{timestamp}] {type_display}")
            print(f"   {thought.content}")
    
    def save_golden_thought(self, thought: Thought):
        """Save a golden thought to a markdown file"""
        timestamp = thought.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"golden_thought_{timestamp}.md"
        
        with open(filename, 'w') as f:
            f.write(f"# Golden Thought - {thought.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Interest Score:** {thought.interest_score:.2f}\n\n")
            f.write(f"**Type:** {thought.thought_type.replace('_', ' ').title()}\n\n")
            f.write(f"**Content:**\n{thought.content}\n\n")
            if thought.tags:
                f.write(f"**Tags:** {', '.join(thought.tags)}\n\n")
    
    def generate_session_summary(self, thoughts: List[Thought]) -> str:
        """Generate a summary of the thinking session"""
        if not thoughts:
            return "No thoughts generated in this session."
        
        total_thoughts = len(thoughts)
        golden_thoughts = [t for t in thoughts if t.thought_type == 'gold_strike']
        avg_interest = sum(t.interest_score for t in thoughts) / total_thoughts
        
        summary = f"""
# Dreaming Session Summary

**Session Duration:** {thoughts[0].timestamp.strftime('%H:%M')} - {thoughts[-1].timestamp.strftime('%H:%M')}
**Total Thoughts:** {total_thoughts}
**Golden Discoveries:** {len(golden_thoughts)}
**Average Interest Score:** {avg_interest:.2f}

## Most Interesting Thoughts:
"""
        
        # Get top 3 most interesting thoughts
        top_thoughts = sorted(thoughts, key=lambda t: t.interest_score, reverse=True)[:3]
        for i, thought in enumerate(top_thoughts, 1):
            summary += f"\n{i}. **{thought.thought_type.replace('_', ' ').title()}** (Score: {thought.interest_score:.2f})\n"
            summary += f"   {thought.content[:200]}{'...' if len(thought.content) > 200 else ''}\n"
        
        return summary


class DreamingAI:
    """Main application class that orchestrates the dreaming process"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.seeder = ThoughtSeeder()
        self.reasoning_engine = ReasoningEngine(
            ollama_url=self.config.get('ollama_url', 'http://localhost:11434'),
            model=self.config.get('model', 'gemma2:2b')
        )
        self.interest_detector = InterestDetector()
        self.memory = MemorySystem(self.config.get('db_path', 'dreaming_memory.db'))
        self.output_manager = OutputManager(self.config.get('output_dir', 'dream_outputs'))
        
        # State management
        self.is_dreaming = False
        self.dream_thread = None
        self.thoughts_generated = []
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "model": "gemma2:2b",
            "ollama_url": "http://localhost:11434",
            "db_path": "dreaming_memory.db",
            "output_dir": "dream_outputs",
            "reasoning_strategies": {
                "free_association": 0.3,
                "logical_deduction": 0.2,
                "creative_what_if": 0.2,
                "pattern_recognition": 0.15,
                "analogical_reasoning": 0.15
            },
            "interest_threshold": 0.4,
            "dream_interval": 5,  # seconds between thoughts
            "max_thoughts_per_session": 100
        }
        
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            # Create default config file
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            print(f"Created default configuration file: {config_path}")
        
        return default_config
    
    def start_dreaming(self):
        """Start the autonomous dreaming process"""
        if self.is_dreaming:
            print("Already dreaming...")
            return
        
        print("🌙 Starting dreaming session...")
        print("Press Ctrl+C to stop dreaming\n")
        
        self.is_dreaming = True
        self.thoughts_generated = []
        
        try:
            self._dream_loop()
        except KeyboardInterrupt:
            print("\n🌅 Dreaming session interrupted by user")
        finally:
            self.stop_dreaming()
    
    def _dream_loop(self):
        """Main dreaming loop - generates thoughts continuously"""
        thought_count = 0
        max_thoughts = self.config.get('max_thoughts_per_session', 100)
        
        # Generate initial seed
        seed_content = self.seeder.generate_seed()
        seed_thought = Thought(
            id=f"thought_{int(time.time() * 1000)}",
            timestamp=datetime.now(),
            content=seed_content,
            thought_type='seed'
        )
        
        self._process_thought(seed_thought)
        thought_count += 1
        
        # Main reasoning loop
        while self.is_dreaming and thought_count < max_thoughts:
            try:
                # Get recent context
                context = self.memory.get_recent_thoughts(10)
                
                # Generate new thought
                new_content = self.reasoning_engine.generate_thought(context)
                
                if new_content:
                    # Create thought object
                    new_thought = Thought(
                        id=f"thought_{int(time.time() * 1000)}_{thought_count}",
                        timestamp=datetime.now(),
                        content=new_content,
                        thought_type='reasoning',
                        parent_id=context[-1].id if context else None
                    )
                    
                    self._process_thought(new_thought)
                    thought_count += 1
                
                # Wait before next thought
                time.sleep(self.config.get('dream_interval', 5))
                
            except Exception as e:
                logging.error(f"Error in dream loop: {e}")
                time.sleep(1)
    
    def _process_thought(self, thought: Thought):
        """Process a single thought - analyze, store, and display"""
        # Calculate interest score
        thought.interest_score = self.interest_detector.calculate_interest_score(thought.content)
        
        # Check if it's a gold strike
        if self.interest_detector.is_gold_strike(thought.content, thought.interest_score):
            thought.thought_type = 'gold_strike'
            self.memory.add_golden_thought(thought, "Autonomous discovery during dreaming")
            self.output_manager.save_golden_thought(thought)
        
        # Store in memory
        self.memory.add_thought(thought)
        self.thoughts_generated.append(thought)
        
        # Display thought
        self.output_manager.display_thought(thought)
    
    def stop_dreaming(self):
        """Stop the dreaming process and generate summary"""
        if not self.is_dreaming:
            return
        
        self.is_dreaming = False
        
        if self.thoughts_generated:
            print(f"\n🌅 Dreaming session completed. Generated {len(self.thoughts_generated)} thoughts.")
            
            # Generate and save session summary
            summary = self.output_manager.generate_session_summary(self.thoughts_generated)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_path = self.output_manager.output_dir / f"session_summary_{timestamp}.md"
            
            with open(summary_path, 'w') as f:
                f.write(summary)
            
            print(f"Session summary saved to: {summary_path}")
            
            # Show golden thoughts if any
            golden_thoughts = [t for t in self.thoughts_generated if t.thought_type == 'gold_strike']
            if golden_thoughts:
                print(f"\n✨ {len(golden_thoughts)} golden discoveries made!")
                for thought in golden_thoughts:
                    print(f"   • {thought.content[:100]}...")
    
    def show_golden_thoughts(self):
        """Display all golden thoughts from memory"""
        golden_thoughts = self.memory.get_golden_thoughts()
        
        if not golden_thoughts:
            print("No golden thoughts discovered yet. Keep dreaming!")
            return
        
        print(f"\n✨ {len(golden_thoughts)} Golden Thoughts Discovered:\n")
        
        for i, thought in enumerate(golden_thoughts, 1):
            print(f"{i}. **Score: {thought['interest_score']:.2f}** - {thought['timestamp']}")
            print(f"   {thought['content']}")
            print(f"   Context: {thought['discovery_context']}")
            print("-" * 60)


def main():
    """Main entry point for the DreamingAI application"""
    print("🧠 DreamingAI - Autonomous Reasoning System")
    print("=" * 50)
    
    # Initialize the dreaming AI
    ai = DreamingAI()
    
    while True:
        print("\nCommands:")
        print("1. start - Begin dreaming session")
        print("2. golden - Show golden thoughts")
        print("3. quit - Exit application")
        
        choice = input("\nEnter command: ").strip().lower()
        
        if choice in ['1', 'start']:
            ai.start_dreaming()
        elif choice in ['2', 'golden']:
            ai.show_golden_thoughts()
        elif choice in ['3', 'quit', 'exit']:
            print("👋 Goodbye! Sweet dreams...")
            break
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()


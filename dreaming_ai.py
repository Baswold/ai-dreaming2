#!/usr/bin/env python3
"""
DreamingAI - A continuous reasoning loop system for local language models

This system runs autonomous reasoning loops without requiring user prompts,
allowing AI models to explore ideas, make connections, and discover insights
through pure thought processes.

Enhanced with web search, advanced reasoning modes, analytics, and more!
"""

import json
import time
import random
import sqlite3
import threading
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, Counter
import logging
import re

import requests
from dataclasses import dataclass, asdict, field

try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    logging.warning("duckduckgo-search not available. Web search disabled.")

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    logging.warning("numpy/sklearn not available. Analytics features disabled.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    logging.warning("matplotlib not available. Plotting features disabled.")

from bs4 import BeautifulSoup


@dataclass
class Thought:
    """Represents a single thought in the reasoning chain"""
    id: str
    timestamp: datetime
    content: str
    thought_type: str  # seed, reasoning, branch, insight, gold_strike, web_search, synthesis
    parent_id: Optional[str] = None
    interest_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    branch_id: Optional[str] = None
    web_sources: List[str] = field(default_factory=list)


@dataclass
class ThoughtBranch:
    """Represents a branch in the reasoning tree"""
    id: str
    parent_thought_id: str
    created_at: datetime
    thoughts: List[Thought] = field(default_factory=list)
    theme: str = ""
    active: bool = True


class WebSearchEngine:
    """Handles web searches for enriching reasoning with external knowledge"""

    def __init__(self, cache_ttl: int = 3600, max_results: int = 3):
        self.cache_ttl = cache_ttl
        self.max_results = max_results
        self.search_cache: Dict[str, Tuple[datetime, List[Dict]]] = {}
        self.search_history: List[Dict] = []

        if not WEB_SEARCH_AVAILABLE:
            logging.warning("Web search functionality not available")

    def search(self, query: str) -> List[Dict]:
        """Perform web search with caching"""
        if not WEB_SEARCH_AVAILABLE:
            return []

        # Check cache first
        cache_key = hashlib.md5(query.encode()).hexdigest()
        if cache_key in self.search_cache:
            cached_time, cached_results = self.search_cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl):
                logging.info(f"Using cached results for: {query}")
                return cached_results

        try:
            logging.info(f"Searching web for: {query}")
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=self.max_results):
                    results.append({
                        'title': r.get('title', ''),
                        'snippet': r.get('body', ''),
                        'url': r.get('href', '')
                    })

                # Cache results
                self.search_cache[cache_key] = (datetime.now(), results)

                # Add to history
                self.search_history.append({
                    'query': query,
                    'timestamp': datetime.now(),
                    'num_results': len(results)
                })

                return results

        except Exception as e:
            logging.error(f"Web search error: {e}")
            return []

    def extract_search_worthy_terms(self, text: str) -> List[str]:
        """Extract terms from text that might be worth searching"""
        # Simple extraction - look for capitalized phrases, questions, and key concepts
        terms = []

        # Extract questions
        questions = re.findall(r'[A-Z][^.?!]*\?', text)
        terms.extend(questions[:2])

        # Extract capitalized phrases (potential proper nouns/concepts)
        capitalized = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        terms.extend(capitalized[:3])

        return list(set(terms))[:2]  # Return up to 2 unique terms

    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for LLM consumption"""
        if not results:
            return "No search results found."

        formatted = "Search Results:\n"
        for i, result in enumerate(results, 1):
            formatted += f"\n{i}. {result['title']}\n"
            formatted += f"   {result['snippet'][:200]}...\n"

        return formatted


class ThoughtSeeder:
    """Generates initial topics and seeds for autonomous reasoning"""

    def __init__(self):
        self.abstract_concepts = [
            "consciousness", "infinity", "emergence", "patterns", "symmetry",
            "chaos", "order", "connection", "transformation", "paradox",
            "beauty", "truth", "existence", "meaning", "purpose", "time",
            "space", "energy", "information", "complexity", "simplicity",
            "entropy", "recursion", "fractals", "dimensions", "causality",
            "perception", "reality", "abstraction", "balance", "harmony"
        ]

        self.concrete_concepts = [
            "ocean", "mountain", "tree", "bird", "crystal", "river", "star",
            "flower", "stone", "wind", "fire", "ice", "light", "shadow",
            "music", "dance", "color", "texture", "sound", "silence",
            "cloud", "wave", "seed", "mirror", "path", "bridge", "door"
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
            "How do we know what we know?",
            "What is the relationship between order and chaos?",
            "How does information create structure?",
            "What role does randomness play in creativity?",
            "Can patterns exist without an observer?",
            "What is the smallest unit of meaning?"
        ]

        self.philosophical_prompts = [
            "Consider the nature of...",
            "What would happen if...",
            "Imagine a world where...",
            "The paradox of...",
            "The hidden connection between...",
            "What if we questioned...",
            "Beyond the surface of...",
            "The essence of..."
        ]

    def generate_seed(self, seed_type: str = None) -> str:
        """Generate a random seed for thinking"""
        if seed_type is None:
            seed_type = random.choice([
                'combination', 'abstract_question', 'timestamp_based',
                'philosophical', 'contrast', 'metaphor'
            ])

        if seed_type == 'combination':
            concept1 = random.choice(self.abstract_concepts + self.concrete_concepts)
            concept2 = random.choice(self.abstract_concepts + self.concrete_concepts)
            while concept2 == concept1:
                concept2 = random.choice(self.abstract_concepts + self.concrete_concepts)
            return f"{concept1} + {concept2}"

        elif seed_type == 'abstract_question':
            return random.choice(self.abstract_questions)

        elif seed_type == 'philosophical':
            prompt = random.choice(self.philosophical_prompts)
            concept = random.choice(self.abstract_concepts)
            return f"{prompt} {concept}"

        elif seed_type == 'contrast':
            concept1 = random.choice(self.abstract_concepts)
            concept2 = random.choice(self.abstract_concepts)
            while concept2 == concept1:
                concept2 = random.choice(self.abstract_concepts)
            return f"The contrast between {concept1} and {concept2}"

        elif seed_type == 'metaphor':
            abstract = random.choice(self.abstract_concepts)
            concrete = random.choice(self.concrete_concepts)
            return f"If {abstract} were a {concrete}, what would it look like?"

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

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma2:2b",
                 web_search_engine: Optional[WebSearchEngine] = None):
        self.ollama_url = ollama_url
        self.model = model
        self.web_search = web_search_engine
        self.reasoning_modes = [
            'free_association',
            'logical_deduction',
            'creative_what_if',
            'pattern_recognition',
            'analogical_reasoning',
            'meta_cognition',
            'synthesis',
            'exploration',
            'web_informed'  # New mode using web search
        ]
        self.error_count = 0
        self.max_retries = 3
        self.performance_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_latency': 0.0
        }

    def generate_thought(self, context: List[Thought], mode: str = None,
                        enable_web_search: bool = False) -> Tuple[str, List[str]]:
        """Generate a new thought based on context and reasoning mode

        Returns:
            Tuple of (thought_content, list_of_web_sources)
        """
        if mode is None:
            # Choose mode based on context
            if enable_web_search and self.web_search and random.random() < 0.2:
                mode = 'web_informed'
            else:
                mode = random.choice([m for m in self.reasoning_modes if m != 'web_informed'])

        # Build context string from recent thoughts
        context_str = ""
        web_sources = []

        if context:
            recent_thoughts = context[-5:]  # Last 5 thoughts for context
            context_str = "\n".join([f"[{t.thought_type.upper()}] {t.content}" for t in recent_thoughts])

        # Handle web-informed reasoning
        web_context = ""
        if mode == 'web_informed' and self.web_search and context:
            # Extract search terms from recent context
            recent_content = " ".join([t.content for t in context[-3:]])
            search_terms = self.web_search.extract_search_worthy_terms(recent_content)

            if search_terms:
                search_query = search_terms[0]
                search_results = self.web_search.search(search_query)
                if search_results:
                    web_context = self.web_search.format_search_results(search_results)
                    web_sources = [r['url'] for r in search_results]

        prompt = self._build_prompt(context_str, mode, web_context)

        # Generate thought with retry logic
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": random.uniform(0.7, 1.2),  # Creativity variance
                            "top_p": 0.9,
                            "max_tokens": 250
                        }
                    },
                    timeout=30
                )

                latency = time.time() - start_time
                self.performance_stats['total_requests'] += 1
                self.performance_stats['total_latency'] += latency

                if response.status_code == 200:
                    self.performance_stats['successful_requests'] += 1
                    self.error_count = 0  # Reset error count on success

                    result = response.json()
                    content = result.get('response', '').strip()
                    return content, web_sources
                else:
                    logging.error(f"Ollama API error: {response.status_code}")

            except requests.exceptions.Timeout:
                logging.error(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

            except Exception as e:
                logging.error(f"Error generating thought: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)

        # Failed after all retries
        self.performance_stats['failed_requests'] += 1
        self.error_count += 1

        # Return fallback thought
        fallback_thoughts = [
            "I notice something interesting about the nature of thought itself...",
            "In this moment of silence, new possibilities emerge...",
            "What if we approached this from a completely different angle?",
            "There's a pattern here that's just beyond my grasp...",
            "Sometimes the most profound insights come from pausing to reflect..."
        ]
        return random.choice(fallback_thoughts), []

    def _build_prompt(self, context: str, mode: str, web_context: str = "") -> str:
        """Build appropriate prompt based on reasoning mode"""
        base_context = f"Previous thoughts:\n{context}\n\n" if context else ""
        web_section = f"\nWeb Research:\n{web_context}\n\n" if web_context else ""

        mode_prompts = {
            'free_association': f"{base_context}Let your mind wander freely. What comes to mind next?",

            'logical_deduction': f"{base_context}Following logical steps, what conclusion emerges?",

            'creative_what_if': f"{base_context}What if we imagined something completely different? What if...",

            'pattern_recognition': f"{base_context}Looking at these ideas, what patterns or connections do you notice?",

            'analogical_reasoning': f"{base_context}How might this be similar to something else entirely? What analogy comes to mind?",

            'meta_cognition': f"{base_context}Stepping back, what do you notice about your own thinking process? What patterns emerge in how ideas are connecting?",

            'synthesis': f"{base_context}How might all these ideas come together? What unified understanding emerges?",

            'exploration': f"{base_context}What unexplored territory lies adjacent to these ideas? What haven't we considered yet?",

            'web_informed': f"{base_context}{web_section}Considering both your thoughts and this external information, what new insights arise?"
        }

        return mode_prompts.get(mode, f"{base_context}What thought arises naturally?")

    def get_performance_summary(self) -> Dict:
        """Get performance statistics"""
        stats = self.performance_stats.copy()
        if stats['successful_requests'] > 0:
            stats['avg_latency'] = stats['total_latency'] / stats['successful_requests']
        else:
            stats['avg_latency'] = 0.0
        return stats


class InterestDetector:
    """Identifies potentially interesting or valuable thoughts"""

    def __init__(self):
        self.interest_keywords = [
            'connection', 'pattern', 'similar', 'like', 'reminds me',
            'what if', 'perhaps', 'maybe', 'could be', 'might',
            'interesting', 'fascinating', 'beautiful', 'elegant',
            'paradox', 'contradiction', 'unexpected', 'surprising',
            'discovery', 'insight', 'realization', 'understanding',
            'relationship', 'correlation', 'analogy', 'metaphor',
            'emerges', 'reveals', 'suggests', 'implies'
        ]

        self.gold_strike_indicators = [
            'breakthrough', 'eureka', 'suddenly clear', 'now I see',
            'this explains', 'the key is', 'fundamental', 'profound',
            'revolutionary', 'paradigm', 'transforms everything',
            'aha', 'revelation', 'illuminates', 'crystallizes'
        ]

        self.semantic_boosters = [
            ('why', 'because'),
            ('question', 'answer'),
            ('problem', 'solution'),
            ('cause', 'effect')
        ]

    def calculate_interest_score(self, thought: str, context: List[Thought] = None) -> float:
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

        # Semantic relationship boosters
        for term1, term2 in self.semantic_boosters:
            if term1 in thought_lower and term2 in thought_lower:
                score += 0.15

        # Length and complexity bonus
        if len(thought) > 100:
            score += 0.1
        if len(thought) > 200:
            score += 0.1

        # Question marks indicate curiosity
        score += min(thought.count('?') * 0.05, 0.15)

        # Exclamation marks indicate excitement/discovery
        score += min(thought.count('!') * 0.1, 0.2)

        # Novelty bonus - if this thought introduces new concepts not in recent context
        if context:
            recent_words = set()
            for t in context[-5:]:
                recent_words.update(t.content.lower().split())

            current_words = set(thought.lower().split())
            new_words = current_words - recent_words

            if len(current_words) > 0:
                novelty_ratio = len(new_words) / len(current_words)
                score += novelty_ratio * 0.2

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
        self.branches: Dict[str, ThoughtBranch] = {}
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
                tags TEXT,
                metadata TEXT,
                branch_id TEXT,
                web_sources TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS golden_thoughts (
                id TEXT PRIMARY KEY,
                timestamp TEXT,
                content TEXT,
                interest_score REAL,
                discovery_context TEXT,
                web_sources TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thought_branches (
                id TEXT PRIMARY KEY,
                parent_thought_id TEXT,
                created_at TEXT,
                theme TEXT,
                active INTEGER
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                total_thoughts INTEGER,
                golden_thoughts INTEGER,
                avg_interest_score REAL,
                summary TEXT
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
            (id, timestamp, content, thought_type, parent_id, interest_score, tags, metadata, branch_id, web_sources)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            thought.id,
            thought.timestamp.isoformat(),
            thought.content,
            thought.thought_type,
            thought.parent_id,
            thought.interest_score,
            json.dumps(thought.tags),
            json.dumps(thought.metadata),
            thought.branch_id,
            json.dumps(thought.web_sources)
        ))

        conn.commit()
        conn.close()

    def add_golden_thought(self, thought: Thought, context: str = ""):
        """Store a particularly interesting thought in the golden collection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO golden_thoughts
            (id, timestamp, content, interest_score, discovery_context, web_sources)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            thought.id,
            thought.timestamp.isoformat(),
            thought.content,
            thought.interest_score,
            context,
            json.dumps(thought.web_sources)
        ))

        conn.commit()
        conn.close()

    def create_branch(self, parent_thought: Thought, theme: str = "") -> ThoughtBranch:
        """Create a new thought branch for divergent exploration"""
        branch = ThoughtBranch(
            id=f"branch_{int(time.time() * 1000)}",
            parent_thought_id=parent_thought.id,
            created_at=datetime.now(),
            theme=theme
        )

        self.branches[branch.id] = branch

        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO thought_branches (id, parent_thought_id, created_at, theme, active)
            VALUES (?, ?, ?, ?, ?)
        ''', (branch.id, branch.parent_thought_id, branch.created_at.isoformat(), branch.theme, 1))

        conn.commit()
        conn.close()

        return branch

    def get_recent_thoughts(self, limit: int = 10) -> List[Thought]:
        """Get recent thoughts from short-term memory"""
        return self.short_term_memory[-limit:]

    def get_golden_thoughts(self, limit: int = None) -> List[Dict]:
        """Retrieve golden thoughts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT id, timestamp, content, interest_score, discovery_context, web_sources
            FROM golden_thoughts
            ORDER BY interest_score DESC, timestamp DESC
        '''

        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query)

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'interest_score': row[3],
                'discovery_context': row[4],
                'web_sources': json.loads(row[5]) if row[5] else []
            })

        conn.close()
        return results

    def get_all_thoughts(self, limit: int = None) -> List[Thought]:
        """Retrieve all thoughts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT id, timestamp, content, thought_type, parent_id, interest_score, tags, metadata, branch_id, web_sources
            FROM thoughts
            ORDER BY timestamp DESC
        '''

        if limit:
            query += f' LIMIT {limit}'

        cursor.execute(query)

        thoughts = []
        for row in cursor.fetchall():
            thought = Thought(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                content=row[2],
                thought_type=row[3],
                parent_id=row[4],
                interest_score=row[5],
                tags=json.loads(row[6]) if row[6] else [],
                metadata=json.loads(row[7]) if row[7] else {},
                branch_id=row[8],
                web_sources=json.loads(row[9]) if row[9] else []
            )
            thoughts.append(thought)

        conn.close()
        return thoughts

    def save_session(self, session_id: str, start_time: datetime, end_time: datetime,
                    thoughts: List[Thought], summary: str):
        """Save session information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        golden_count = sum(1 for t in thoughts if t.thought_type == 'gold_strike')
        avg_score = sum(t.interest_score for t in thoughts) / len(thoughts) if thoughts else 0

        cursor.execute('''
            INSERT INTO sessions (id, start_time, end_time, total_thoughts, golden_thoughts, avg_interest_score, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, start_time.isoformat(), end_time.isoformat(),
              len(thoughts), golden_count, avg_score, summary))

        conn.commit()
        conn.close()


class ThoughtAnalyzer:
    """Analyzes thought patterns and generates insights"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100) if ANALYTICS_AVAILABLE else None

    def cluster_thoughts(self, thoughts: List[Thought], n_clusters: int = 5) -> Dict[int, List[Thought]]:
        """Cluster thoughts by semantic similarity"""
        if not ANALYTICS_AVAILABLE or not thoughts or len(thoughts) < n_clusters:
            return {0: thoughts}

        try:
            # Extract text content
            texts = [t.content for t in thoughts]

            # Vectorize
            X = self.vectorizer.fit_transform(texts)

            # Cluster
            kmeans = KMeans(n_clusters=min(n_clusters, len(thoughts)), random_state=42)
            labels = kmeans.fit_predict(X)

            # Group by cluster
            clusters = defaultdict(list)
            for thought, label in zip(thoughts, labels):
                clusters[int(label)].append(thought)

            return dict(clusters)

        except Exception as e:
            logging.error(f"Clustering error: {e}")
            return {0: thoughts}

    def extract_themes(self, thoughts: List[Thought], top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract common themes from thoughts"""
        # Simple word frequency analysis
        word_counts = Counter()

        # Common stop words to filter
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                     'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those',
                     'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when',
                     'where', 'why', 'how', 'if', 'then', 'than', 'so', 'just', 'now'}

        for thought in thoughts:
            words = re.findall(r'\b[a-z]{4,}\b', thought.content.lower())
            for word in words:
                if word not in stop_words:
                    word_counts[word] += 1

        return word_counts.most_common(top_n)

    def analyze_interest_evolution(self, thoughts: List[Thought]) -> Dict:
        """Analyze how interest scores evolve over time"""
        if not thoughts:
            return {}

        scores = [t.interest_score for t in thoughts]

        return {
            'mean': np.mean(scores) if ANALYTICS_AVAILABLE else sum(scores) / len(scores),
            'std': np.std(scores) if ANALYTICS_AVAILABLE else 0,
            'min': min(scores),
            'max': max(scores),
            'trend': 'increasing' if scores[-1] > scores[0] else 'decreasing'
        }


class OutputManager:
    """Manages display and saving of thoughts and discoveries"""

    def __init__(self, output_dir: str = "dream_outputs", verbose: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.verbose = verbose

        # Setup logging
        log_level = logging.INFO if verbose else logging.WARNING
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.output_dir / 'dreaming.log'),
                logging.StreamHandler()
            ]
        )

    def display_thought(self, thought: Thought):
        """Display a thought to console with formatting"""
        if not self.verbose:
            return

        timestamp = thought.timestamp.strftime("%H:%M:%S")
        type_display = thought.thought_type.upper().replace('_', ' ')

        if thought.thought_type == 'gold_strike':
            print(f"\n🌟 [{timestamp}] {type_display} (Score: {thought.interest_score:.2f})")
            print(f"✨ {thought.content}")
            if thought.web_sources:
                print(f"📚 Sources: {', '.join(thought.web_sources[:2])}")
            print("=" * 60)
        elif thought.interest_score > 0.4:
            print(f"\n💡 [{timestamp}] {type_display} (Score: {thought.interest_score:.2f})")
            print(f"   {thought.content}")
            if thought.web_sources:
                print(f"   📚 Web-informed")
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

            if thought.web_sources:
                f.write(f"**Web Sources:**\n")
                for source in thought.web_sources:
                    f.write(f"- {source}\n")
                f.write("\n")

            if thought.tags:
                f.write(f"**Tags:** {', '.join(thought.tags)}\n\n")

    def generate_session_summary(self, thoughts: List[Thought], performance_stats: Dict = None) -> str:
        """Generate a summary of the thinking session"""
        if not thoughts:
            return "No thoughts generated in this session."

        total_thoughts = len(thoughts)
        golden_thoughts = [t for t in thoughts if t.thought_type == 'gold_strike']
        web_informed = [t for t in thoughts if t.web_sources]
        avg_interest = sum(t.interest_score for t in thoughts) / total_thoughts

        # Type distribution
        type_counts = Counter(t.thought_type for t in thoughts)

        summary = f"""
# Dreaming Session Summary

**Session Duration:** {thoughts[0].timestamp.strftime('%H:%M')} - {thoughts[-1].timestamp.strftime('%H:%M')}
**Total Thoughts:** {total_thoughts}
**Golden Discoveries:** {len(golden_thoughts)}
**Web-Informed Thoughts:** {len(web_informed)}
**Average Interest Score:** {avg_interest:.2f}

## Thought Type Distribution:
"""
        for thought_type, count in type_counts.most_common():
            summary += f"- {thought_type.replace('_', ' ').title()}: {count}\n"

        if performance_stats:
            summary += f"\n## Performance Statistics:\n"
            summary += f"- Total API Requests: {performance_stats.get('total_requests', 0)}\n"
            summary += f"- Successful: {performance_stats.get('successful_requests', 0)}\n"
            summary += f"- Failed: {performance_stats.get('failed_requests', 0)}\n"
            summary += f"- Average Latency: {performance_stats.get('avg_latency', 0):.2f}s\n"

        summary += "\n## Most Interesting Thoughts:\n"

        # Get top 5 most interesting thoughts
        top_thoughts = sorted(thoughts, key=lambda t: t.interest_score, reverse=True)[:5]
        for i, thought in enumerate(top_thoughts, 1):
            summary += f"\n{i}. **{thought.thought_type.replace('_', ' ').title()}** (Score: {thought.interest_score:.2f})\n"
            summary += f"   {thought.content[:200]}{'...' if len(thought.content) > 200 else ''}\n"

        return summary

    def export_to_json(self, thoughts: List[Thought], filename: str = "thoughts_export.json"):
        """Export thoughts to JSON format"""
        export_path = self.output_dir / filename

        data = {
            'export_time': datetime.now().isoformat(),
            'total_thoughts': len(thoughts),
            'thoughts': [
                {
                    'id': t.id,
                    'timestamp': t.timestamp.isoformat(),
                    'content': t.content,
                    'type': t.thought_type,
                    'interest_score': t.interest_score,
                    'tags': t.tags,
                    'web_sources': t.web_sources
                }
                for t in thoughts
            ]
        }

        with open(export_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Exported {len(thoughts)} thoughts to {export_path}")

    def create_visualization(self, thoughts: List[Thought], filename: str = "thought_analysis.png"):
        """Create visualizations of thought patterns"""
        if not PLOTTING_AVAILABLE or not thoughts:
            logging.warning("Plotting not available or no thoughts to visualize")
            return

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        # 1. Interest score over time
        timestamps = [t.timestamp for t in thoughts]
        scores = [t.interest_score for t in thoughts]

        ax1.plot(timestamps, scores, marker='o', linestyle='-', alpha=0.7)
        ax1.set_title('Interest Score Over Time')
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Interest Score')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # 2. Thought type distribution
        type_counts = Counter(t.thought_type for t in thoughts)
        ax2.bar(range(len(type_counts)), list(type_counts.values()))
        ax2.set_title('Thought Type Distribution')
        ax2.set_xlabel('Thought Type')
        ax2.set_ylabel('Count')
        ax2.set_xticks(range(len(type_counts)))
        ax2.set_xticklabels([t.replace('_', '\n') for t in type_counts.keys()], rotation=45, ha='right')

        # 3. Interest score distribution
        ax3.hist(scores, bins=20, edgecolor='black', alpha=0.7)
        ax3.set_title('Interest Score Distribution')
        ax3.set_xlabel('Interest Score')
        ax3.set_ylabel('Frequency')
        ax3.axvline(np.mean(scores) if ANALYTICS_AVAILABLE else sum(scores)/len(scores),
                   color='red', linestyle='--', label='Mean')
        ax3.legend()

        # 4. Thought length over time
        lengths = [len(t.content) for t in thoughts]
        ax4.scatter(timestamps, lengths, alpha=0.6)
        ax4.set_title('Thought Length Over Time')
        ax4.set_xlabel('Time')
        ax4.set_ylabel('Characters')
        ax4.grid(True, alpha=0.3)
        ax4.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        plt.tight_layout()

        output_path = self.output_dir / filename
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Visualization saved to {output_path}")


class DreamingAI:
    """Main application class that orchestrates the dreaming process"""

    def __init__(self, config_path: str = "config.json", verbose: bool = True):
        self.config = self._load_config(config_path)
        self.verbose = verbose

        # Initialize components
        self.seeder = ThoughtSeeder()

        # Initialize web search if enabled
        self.web_search = None
        if self.config.get('enable_web_search', True) and WEB_SEARCH_AVAILABLE:
            self.web_search = WebSearchEngine(
                cache_ttl=self.config.get('web_search_cache_ttl', 3600),
                max_results=self.config.get('web_search_max_results', 3)
            )

        self.reasoning_engine = ReasoningEngine(
            ollama_url=self.config.get('ollama_url', 'http://localhost:11434'),
            model=self.config.get('model', 'gemma2:2b'),
            web_search_engine=self.web_search
        )

        self.interest_detector = InterestDetector()
        self.memory = MemorySystem(self.config.get('db_path', 'dreaming_memory.db'))
        self.output_manager = OutputManager(
            self.config.get('output_dir', 'dream_outputs'),
            verbose=verbose
        )
        self.analyzer = ThoughtAnalyzer()

        # State management
        self.is_dreaming = False
        self.dream_thread = None
        self.thoughts_generated = []
        self.session_id = None
        self.session_start_time = None

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        default_config = {
            "model": "gemma2:2b",
            "ollama_url": "http://localhost:11434",
            "db_path": "dreaming_memory.db",
            "output_dir": "dream_outputs",
            "reasoning_strategies": {
                "free_association": 0.25,
                "logical_deduction": 0.15,
                "creative_what_if": 0.15,
                "pattern_recognition": 0.15,
                "analogical_reasoning": 0.1,
                "meta_cognition": 0.1,
                "synthesis": 0.05,
                "exploration": 0.05
            },
            "interest_threshold": 0.4,
            "dream_interval": 5,
            "max_thoughts_per_session": 100,
            "enable_web_search": True,
            "web_search_cache_ttl": 3600,
            "web_search_max_results": 3,
            "enable_branching": False,
            "branch_probability": 0.1
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

    def start_dreaming(self, max_thoughts: int = None):
        """Start the autonomous dreaming process"""
        if self.is_dreaming:
            print("Already dreaming...")
            return

        print("🌙 Starting dreaming session...")
        if self.web_search:
            print("🌐 Web search enabled")
        print("Press Ctrl+C to stop dreaming\n")

        self.is_dreaming = True
        self.thoughts_generated = []
        self.session_id = f"session_{int(time.time() * 1000)}"
        self.session_start_time = datetime.now()

        try:
            self._dream_loop(max_thoughts or self.config.get('max_thoughts_per_session', 100))
        except KeyboardInterrupt:
            print("\n🌅 Dreaming session interrupted by user")
        finally:
            self.stop_dreaming()

    def _dream_loop(self, max_thoughts: int):
        """Main dreaming loop - generates thoughts continuously"""
        thought_count = 0

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

                # Determine if we should use web search
                enable_web = (
                    self.web_search is not None and
                    random.random() < 0.2  # 20% chance for web-informed thoughts
                )

                # Generate new thought
                new_content, web_sources = self.reasoning_engine.generate_thought(
                    context,
                    enable_web_search=enable_web
                )

                if new_content:
                    # Create thought object
                    new_thought = Thought(
                        id=f"thought_{int(time.time() * 1000)}_{thought_count}",
                        timestamp=datetime.now(),
                        content=new_content,
                        thought_type='web_search' if web_sources else 'reasoning',
                        parent_id=context[-1].id if context else None,
                        web_sources=web_sources
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
        # Calculate interest score with context
        context = self.memory.get_recent_thoughts(5)
        thought.interest_score = self.interest_detector.calculate_interest_score(
            thought.content,
            context
        )

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

            # Get performance stats
            perf_stats = self.reasoning_engine.get_performance_summary()

            # Generate and save session summary
            summary = self.output_manager.generate_session_summary(
                self.thoughts_generated,
                perf_stats
            )
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_path = self.output_manager.output_dir / f"session_summary_{timestamp}.md"

            with open(summary_path, 'w') as f:
                f.write(summary)

            print(f"Session summary saved to: {summary_path}")

            # Save session to database
            self.memory.save_session(
                self.session_id,
                self.session_start_time,
                datetime.now(),
                self.thoughts_generated,
                summary
            )

            # Show golden thoughts if any
            golden_thoughts = [t for t in self.thoughts_generated if t.thought_type == 'gold_strike']
            if golden_thoughts:
                print(f"\n✨ {len(golden_thoughts)} golden discoveries made!")
                for thought in golden_thoughts:
                    print(f"   • {thought.content[:100]}...")

            # Analyze themes
            print("\n🎨 Analyzing thought patterns...")
            themes = self.analyzer.extract_themes(self.thoughts_generated, top_n=5)
            if themes:
                print("\nTop themes:")
                for theme, count in themes[:5]:
                    print(f"   • {theme}: {count}")

    def show_golden_thoughts(self, limit: int = 10):
        """Display golden thoughts from memory"""
        golden_thoughts = self.memory.get_golden_thoughts(limit=limit)

        if not golden_thoughts:
            print("No golden thoughts discovered yet. Keep dreaming!")
            return

        print(f"\n✨ {len(golden_thoughts)} Golden Thoughts Discovered:\n")

        for i, thought in enumerate(golden_thoughts, 1):
            print(f"{i}. **Score: {thought['interest_score']:.2f}** - {thought['timestamp']}")
            print(f"   {thought['content'][:150]}{'...' if len(thought['content']) > 150 else ''}")
            if thought['web_sources']:
                print(f"   📚 Web-informed: {len(thought['web_sources'])} sources")
            print("-" * 60)

    def analyze_thoughts(self):
        """Analyze all thoughts and display insights"""
        print("\n🔍 Analyzing all thoughts in database...")

        thoughts = self.memory.get_all_thoughts(limit=1000)

        if not thoughts:
            print("No thoughts to analyze yet.")
            return

        print(f"\nTotal thoughts in database: {len(thoughts)}")

        # Cluster analysis
        print("\n📊 Clustering thoughts...")
        clusters = self.analyzer.cluster_thoughts(thoughts, n_clusters=5)
        print(f"Found {len(clusters)} clusters:")
        for cluster_id, cluster_thoughts in clusters.items():
            print(f"\nCluster {cluster_id + 1}: {len(cluster_thoughts)} thoughts")
            if cluster_thoughts:
                # Show most representative thought (highest interest score)
                rep_thought = max(cluster_thoughts, key=lambda t: t.interest_score)
                print(f"  Representative: {rep_thought.content[:100]}...")

        # Theme extraction
        print("\n🎨 Top themes across all thoughts:")
        themes = self.analyzer.extract_themes(thoughts, top_n=15)
        for i, (theme, count) in enumerate(themes, 1):
            print(f"{i:2d}. {theme}: {count}")

        # Interest evolution
        print("\n📈 Interest score statistics:")
        stats = self.analyzer.analyze_interest_evolution(thoughts)
        print(f"  Mean: {stats['mean']:.3f}")
        print(f"  Min: {stats['min']:.3f}")
        print(f"  Max: {stats['max']:.3f}")
        print(f"  Trend: {stats['trend']}")

        # Create visualization
        if PLOTTING_AVAILABLE:
            print("\n📊 Creating visualization...")
            self.output_manager.create_visualization(thoughts)

    def export_data(self, format: str = 'json'):
        """Export thought data in various formats"""
        print(f"\n💾 Exporting data in {format} format...")

        thoughts = self.memory.get_all_thoughts()

        if format == 'json':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_manager.export_to_json(thoughts, f"thoughts_export_{timestamp}.json")
        else:
            print(f"Format '{format}' not supported yet.")


def main():
    """Main entry point for the DreamingAI application"""
    parser = argparse.ArgumentParser(
        description="🧠 DreamingAI - Autonomous Reasoning System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.json',
        help='Path to configuration file'
    )

    parser.add_argument(
        '--auto-start',
        action='store_true',
        help='Automatically start dreaming without menu'
    )

    parser.add_argument(
        '--max-thoughts',
        type=int,
        help='Maximum thoughts per session'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Minimal output mode'
    )

    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze existing thoughts and exit'
    )

    parser.add_argument(
        '--export',
        type=str,
        choices=['json'],
        help='Export data and exit'
    )

    args = parser.parse_args()

    print("🧠 DreamingAI - Autonomous Reasoning System")
    print("=" * 50)

    # Initialize the dreaming AI
    ai = DreamingAI(config_path=args.config, verbose=not args.quiet)

    # Handle special modes
    if args.analyze:
        ai.analyze_thoughts()
        return

    if args.export:
        ai.export_data(format=args.export)
        return

    if args.auto_start:
        ai.start_dreaming(max_thoughts=args.max_thoughts)
        return

    # Interactive mode
    while True:
        print("\nCommands:")
        print("1. start    - Begin dreaming session")
        print("2. golden   - Show golden thoughts")
        print("3. analyze  - Analyze thought patterns")
        print("4. export   - Export thoughts to JSON")
        print("5. viz      - Create visualizations")
        print("6. quit     - Exit application")

        choice = input("\nEnter command: ").strip().lower()

        if choice in ['1', 'start']:
            ai.start_dreaming(max_thoughts=args.max_thoughts)
        elif choice in ['2', 'golden']:
            ai.show_golden_thoughts()
        elif choice in ['3', 'analyze']:
            ai.analyze_thoughts()
        elif choice in ['4', 'export']:
            ai.export_data(format='json')
        elif choice in ['5', 'viz']:
            thoughts = ai.memory.get_all_thoughts()
            if thoughts:
                ai.output_manager.create_visualization(thoughts)
            else:
                print("No thoughts to visualize yet.")
        elif choice in ['6', 'quit', 'exit', 'q']:
            print("👋 Goodbye! Sweet dreams...")
            break
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()

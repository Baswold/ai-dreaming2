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
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from urllib.parse import quote_plus, urljoin
from html.parser import HTMLParser

import requests
from dataclasses import dataclass, asdict, field


@dataclass
class Thought:
    """Represents a single thought in the reasoning chain"""
    id: str
    timestamp: datetime
    content: str
    thought_type: str  # seed, reasoning, branch, insight, gold_strike, web_search
    parent_id: Optional[str] = None
    interest_score: float = 0.0
    tags: List[str] = None
    search_query: Optional[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class SearchResult:
    """Represents a web search result"""
    title: str
    snippet: str
    url: str
    source: str  # 'duckduckgo', 'wikipedia', etc.
    timestamp: datetime = field(default_factory=datetime.now)


class HTMLTextExtractor(HTMLParser):
    """Extract text content from HTML"""
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ''.join(self.text)


class SearchCache:
    """Cache search results to avoid repeated queries"""

    def __init__(self, cache_duration_hours: int = 24, db_path: str = "dreaming_memory.db"):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.db_path = db_path
        self._init_cache_table()

    def _init_cache_table(self):
        """Initialize cache table in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT,
                results TEXT,
                timestamp TEXT,
                source TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def _hash_query(self, query: str) -> str:
        """Generate hash for query"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()

    def get(self, query: str) -> Optional[List[SearchResult]]:
        """Retrieve cached results if available and not expired"""
        query_hash = self._hash_query(query)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT results, timestamp, source FROM search_cache
            WHERE query_hash = ?
        ''', (query_hash,))

        row = cursor.fetchone()
        conn.close()

        if row:
            results_json, timestamp_str, source = row
            cached_time = datetime.fromisoformat(timestamp_str)

            # Check if cache is still valid
            if datetime.now() - cached_time < self.cache_duration:
                results_data = json.loads(results_json)
                return [
                    SearchResult(
                        title=r['title'],
                        snippet=r['snippet'],
                        url=r['url'],
                        source=r['source'],
                        timestamp=datetime.fromisoformat(r['timestamp'])
                    )
                    for r in results_data
                ]

        return None

    def set(self, query: str, results: List[SearchResult], source: str = "unknown"):
        """Cache search results"""
        query_hash = self._hash_query(query)
        results_json = json.dumps([
            {
                'title': r.title,
                'snippet': r.snippet,
                'url': r.url,
                'source': r.source,
                'timestamp': r.timestamp.isoformat()
            }
            for r in results
        ])

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO search_cache
            (query_hash, query, results, timestamp, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (query_hash, query, results_json, datetime.now().isoformat(), source))

        conn.commit()
        conn.close()


class CuriosityDetector:
    """Detects when the AI is curious and might want to search for information"""

    def __init__(self):
        self.curiosity_keywords = [
            'what is', 'who is', 'when did', 'where is', 'why does',
            'how does', 'how can', 'I wonder', 'curious about',
            'tell me about', 'learn more about', 'find out about',
            'what are', 'who are', 'explain', 'wondering',
            'want to know', 'interested in', 'more information',
            'research', 'investigate', 'explore', 'discover'
        ]

        self.question_patterns = [
            r'\bwhat\s+(?:is|are|was|were)\b',
            r'\bwho\s+(?:is|are|was|were)\b',
            r'\bwhere\s+(?:is|are|was|were)\b',
            r'\bwhen\s+(?:did|do|does)\b',
            r'\bhow\s+(?:does|do|did|can|could)\b',
            r'\bwhy\s+(?:is|are|do|does|did)\b',
        ]

    def detect_curiosity(self, thought: str) -> Tuple[bool, Optional[str]]:
        """
        Detect if thought expresses curiosity and extract search query.
        Returns (is_curious, extracted_query)
        """
        thought_lower = thought.lower()

        # Check for direct curiosity keywords
        for keyword in self.curiosity_keywords:
            if keyword in thought_lower:
                # Extract potential search query
                query = self._extract_query(thought, keyword)
                if query:
                    return (True, query)

        # Check for question patterns
        for pattern in self.question_patterns:
            match = re.search(pattern, thought_lower)
            if match:
                # Extract the question as query
                query = self._extract_question_query(thought)
                if query:
                    return (True, query)

        # Check if thought ends with a question mark
        if '?' in thought:
            query = self._extract_question_query(thought)
            if query:
                return (True, query)

        return (False, None)

    def _extract_query(self, thought: str, keyword: str) -> Optional[str]:
        """Extract search query from thought containing curiosity keyword"""
        thought_lower = thought.lower()
        keyword_pos = thought_lower.find(keyword)

        if keyword_pos == -1:
            return None

        # Get text after keyword
        after_keyword = thought[keyword_pos + len(keyword):].strip()

        # Clean up the query
        query = after_keyword.split('.')[0].split('?')[0].split(',')[0].split(';')[0].strip()

        # Remove common stop words at the start
        stop_words = ['the', 'a', 'an', 'about', 'more', 'of']
        words = query.split()
        while words and words[0].lower() in stop_words:
            words.pop(0)

        query = ' '.join(words)

        # Return query if it's substantial enough (lowered threshold for better detection)
        return query if len(query) > 3 else None

    def _extract_question_query(self, thought: str) -> Optional[str]:
        """Extract search query from a question"""
        # Find question sentences
        sentences = re.split(r'[.!]\s+', thought)

        for sentence in sentences:
            if '?' in sentence:
                query = sentence.replace('?', '').strip()
                # Clean up
                query = re.sub(r'\s+', ' ', query)
                return query if len(query) > 5 else None

        return None


class WebSearchEngine:
    """Handles web searches through multiple backends"""

    def __init__(self, cache_duration_hours: int = 24, db_path: str = "dreaming_memory.db",
                 rate_limit_delay: float = 1.0, max_retries: int = 3):
        self.cache = SearchCache(cache_duration_hours, db_path)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.rate_limit_delay = rate_limit_delay
        self.max_retries = max_retries
        self.last_search_time = None

    def search(self, query: str, max_results: int = 3, prefer_source: str = 'auto') -> List[SearchResult]:
        """
        Perform web search using available backends.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            prefer_source: Preferred source ('duckduckgo', 'wikipedia', 'auto')

        Returns:
            List of SearchResult objects
        """
        # Check cache first
        cached_results = self.cache.get(query)
        if cached_results:
            logging.info(f"Using cached search results for: {query}")
            return cached_results[:max_results]

        # Apply rate limiting
        self._apply_rate_limit()

        results = []

        # Determine which source to use
        if prefer_source == 'auto':
            # Use Wikipedia for factual/encyclopedia queries
            if self._is_encyclopedic_query(query):
                prefer_source = 'wikipedia'
            else:
                prefer_source = 'duckduckgo'

        # Try primary source with retries
        try:
            if prefer_source == 'wikipedia':
                results = self._search_with_retry(self._search_wikipedia, query, max_results)
            else:
                results = self._search_with_retry(self._search_duckduckgo, query, max_results)
        except Exception as e:
            logging.warning(f"Primary search source failed after retries: {e}")

        # Fallback to alternative source if primary failed
        if not results:
            try:
                if prefer_source == 'wikipedia':
                    results = self._search_with_retry(self._search_duckduckgo, query, max_results)
                else:
                    results = self._search_with_retry(self._search_wikipedia, query, max_results)
            except Exception as e:
                logging.warning(f"Fallback search source failed after retries: {e}")

        # Cache results if we got any
        if results:
            self.cache.set(query, results, source=prefer_source)

        return results

    def _apply_rate_limit(self):
        """Apply rate limiting between searches"""
        if self.last_search_time is not None:
            time_since_last = time.time() - self.last_search_time
            if time_since_last < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - time_since_last
                logging.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                time.sleep(sleep_time)
        self.last_search_time = time.time()

    def _search_with_retry(self, search_func, query: str, max_results: int) -> List[SearchResult]:
        """Execute search with retry logic"""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                results = search_func(query, max_results)
                if results:
                    return results
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logging.warning(f"Search attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)

        # If all retries failed, raise the last exception
        if last_exception:
            raise last_exception

        return []

    def _is_encyclopedic_query(self, query: str) -> bool:
        """Determine if query is better suited for Wikipedia"""
        encyclopedic_indicators = [
            'what is', 'who is', 'what are', 'who are',
            'define', 'definition of', 'meaning of',
            'history of', 'biography', 'explain'
        ]
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in encyclopedic_indicators)

    def _search_duckduckgo(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """Search using DuckDuckGo HTML interface"""
        try:
            # Use DuckDuckGo HTML interface
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(url, timeout=10)

            if response.status_code != 200:
                logging.error(f"DuckDuckGo returned status code: {response.status_code}")
                return []

            # Parse HTML to extract results
            html_content = response.text
            results = []

            # Simple regex-based parsing for DuckDuckGo HTML results
            # Look for result blocks
            result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?<a[^>]*class="result__snippet"[^>]*>(.*?)</a>'
            matches = re.findall(result_pattern, html_content, re.DOTALL)

            for match in matches[:max_results]:
                url, title_html, snippet_html = match

                # Clean HTML from title and snippet
                title = self._clean_html(title_html)
                snippet = self._clean_html(snippet_html)

                # Decode URL
                url = url.replace('&amp;', '&')

                if title and snippet:
                    results.append(SearchResult(
                        title=title.strip(),
                        snippet=snippet.strip(),
                        url=url.strip(),
                        source='duckduckgo'
                    ))

            return results

        except Exception as e:
            logging.error(f"DuckDuckGo search error: {e}")
            return []

    def _search_wikipedia(self, query: str, max_results: int = 3) -> List[SearchResult]:
        """Search using Wikipedia API"""
        try:
            # Wikipedia API search
            api_url = "https://en.wikipedia.org/w/api.php"
            params = {
                'action': 'opensearch',
                'search': query,
                'limit': max_results,
                'format': 'json',
                'namespace': 0
            }

            response = self.session.get(api_url, params=params, timeout=10)

            if response.status_code != 200:
                logging.error(f"Wikipedia API returned status code: {response.status_code}")
                return []

            data = response.json()

            # Wikipedia API returns: [query, [titles], [descriptions], [urls]]
            if len(data) < 4:
                return []

            titles = data[1]
            descriptions = data[2]
            urls = data[3]

            results = []
            for i in range(min(len(titles), max_results)):
                if titles[i] and urls[i]:
                    results.append(SearchResult(
                        title=titles[i],
                        snippet=descriptions[i] if descriptions[i] else "Wikipedia article",
                        url=urls[i],
                        source='wikipedia'
                    ))

            return results

        except Exception as e:
            logging.error(f"Wikipedia search error: {e}")
            return []

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags and decode entities"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html_text)
        # Decode common HTML entities
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        text = text.replace('&nbsp;', ' ')
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


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

    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma2:2b",
                 enable_web_search: bool = True, db_path: str = "dreaming_memory.db"):
        self.ollama_url = ollama_url
        self.model = model
        self.enable_web_search = enable_web_search
        self.reasoning_modes = [
            'free_association',
            'logical_deduction',
            'creative_what_if',
            'pattern_recognition',
            'analogical_reasoning'
        ]

        # Add web search mode if enabled
        if enable_web_search:
            self.reasoning_modes.append('curiosity_driven_search')
            self.web_search = WebSearchEngine(db_path=db_path)
            self.curiosity_detector = CuriosityDetector()
        else:
            self.web_search = None
            self.curiosity_detector = None
    
    def generate_thought(self, context: List[Thought], mode: str = None) -> Tuple[str, Optional[str], Optional[List[SearchResult]]]:
        """
        Generate a new thought based on context and reasoning mode.

        Returns:
            Tuple of (thought_content, search_query, search_results)
        """
        if mode is None:
            mode = random.choice(self.reasoning_modes)

        # Build context string from recent thoughts
        context_str = ""
        if context:
            recent_thoughts = context[-5:]  # Last 5 thoughts for context
            context_str = "\n".join([f"[{t.thought_type.upper()}] {t.content}" for t in recent_thoughts])

        # Handle curiosity-driven search mode
        if mode == 'curiosity_driven_search' and self.enable_web_search:
            return self._generate_curiosity_driven_thought(context, context_str)

        # Check if the last thought expressed curiosity
        search_query = None
        search_results = None
        if self.enable_web_search and context:
            last_thought = context[-1]
            is_curious, extracted_query = self.curiosity_detector.detect_curiosity(last_thought.content)

            if is_curious and extracted_query:
                # Perform web search
                search_query = extracted_query
                search_results = self.web_search.search(extracted_query, max_results=3)

                if search_results:
                    # Generate thought informed by search results
                    return self._generate_search_informed_thought(context_str, search_query, search_results, mode)

        # Normal thought generation
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
                thought_content = result.get('response', '').strip()
                return (thought_content, None, None)
            else:
                logging.error(f"Ollama API error: {response.status_code}")
                return ("I notice something interesting about the nature of thought itself...", None, None)

        except Exception as e:
            logging.error(f"Error generating thought: {e}")
            return ("In this moment of silence, new possibilities emerge...", None, None)

    def _generate_curiosity_driven_thought(self, context: List[Thought], context_str: str) -> Tuple[str, Optional[str], Optional[List[SearchResult]]]:
        """Generate a thought that naturally leads to curiosity and search"""
        # Generate a curious question first
        prompt = f"{context_str}\n\nExpress genuine curiosity about something. Ask a question about something you'd like to learn more about."

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.9,
                        "top_p": 0.9,
                        "max_tokens": 150
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                curious_thought = result.get('response', '').strip()

                # Try to extract a search query from this curious thought
                is_curious, search_query = self.curiosity_detector.detect_curiosity(curious_thought)

                if is_curious and search_query:
                    # Perform the search
                    search_results = self.web_search.search(search_query, max_results=3)

                    if search_results:
                        # Generate a follow-up thought informed by the search results
                        search_summary = self._format_search_results(search_results)
                        follow_up_prompt = f"{curious_thought}\n\nSearch results:\n{search_summary}\n\nBased on this information, what's your next thought?"

                        follow_up_response = requests.post(
                            f"{self.ollama_url}/api/generate",
                            json={
                                "model": self.model,
                                "prompt": follow_up_prompt,
                                "stream": False,
                                "options": {
                                    "temperature": 0.8,
                                    "top_p": 0.9,
                                    "max_tokens": 200
                                }
                            },
                            timeout=30
                        )

                        if follow_up_response.status_code == 200:
                            follow_up_result = follow_up_response.json()
                            follow_up_thought = follow_up_result.get('response', '').strip()
                            # Combine the curious question with the informed response
                            combined_thought = f"{curious_thought}\n\n{follow_up_thought}"
                            return (combined_thought, search_query, search_results)

                return (curious_thought, search_query, search_results if search_query else None)

        except Exception as e:
            logging.error(f"Error in curiosity-driven thought: {e}")

        return ("I wonder about something I've never considered before...", None, None)

    def _generate_search_informed_thought(self, context_str: str, search_query: str,
                                         search_results: List[SearchResult], mode: str) -> Tuple[str, str, List[SearchResult]]:
        """Generate a thought informed by web search results"""
        search_summary = self._format_search_results(search_results)

        prompt = f"{context_str}\n\nYou wondered about: {search_query}\n\nHere's what was found:\n{search_summary}\n\nReflect on this new information. What insights or connections do you notice?"

        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "max_tokens": 250
                    }
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                thought_content = result.get('response', '').strip()
                return (thought_content, search_query, search_results)

        except Exception as e:
            logging.error(f"Error generating search-informed thought: {e}")

        # Fallback
        return (f"Interesting findings about {search_query}...", search_query, search_results)

    def _format_search_results(self, results: List[SearchResult]) -> str:
        """Format search results for inclusion in prompts"""
        formatted = []
        for i, result in enumerate(results[:3], 1):
            formatted.append(f"{i}. {result.title}\n   {result.snippet}\n   Source: {result.source}")
        return "\n\n".join(formatted)
    
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
                tags TEXT,
                search_query TEXT
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
            (id, timestamp, content, thought_type, parent_id, interest_score, tags, search_query)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            thought.id,
            thought.timestamp.isoformat(),
            thought.content,
            thought.thought_type,
            thought.parent_id,
            thought.interest_score,
            json.dumps(thought.tags),
            thought.search_query
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
    
    def display_thought(self, thought: Thought, search_results: Optional[List[SearchResult]] = None):
        """Display a thought to console with formatting"""
        timestamp = thought.timestamp.strftime("%H:%M:%S")
        type_display = thought.thought_type.upper().replace('_', ' ')

        if thought.thought_type == 'gold_strike':
            print(f"\n🌟 [{timestamp}] {type_display} (Score: {thought.interest_score:.2f})")
            print(f"✨ {thought.content}")
            if thought.search_query:
                print(f"🔍 Searched: {thought.search_query}")
            print("=" * 60)
        elif thought.thought_type == 'web_search':
            print(f"\n🔍 [{timestamp}] {type_display}")
            print(f"   Query: {thought.search_query}")
            print(f"   {thought.content}")
            if search_results:
                print(f"\n   📚 Found {len(search_results)} results:")
                for i, result in enumerate(search_results[:3], 1):
                    print(f"   {i}. {result.title} ({result.source})")
                    print(f"      {result.snippet[:100]}...")
        elif thought.interest_score > 0.4:
            print(f"\n💡 [{timestamp}] {type_display} (Score: {thought.interest_score:.2f})")
            print(f"   {thought.content}")
            if thought.search_query:
                print(f"   🔍 Searched: {thought.search_query}")
        else:
            print(f"\n💭 [{timestamp}] {type_display}")
            print(f"   {thought.content}")
            if thought.search_query:
                print(f"   🔍 Searched: {thought.search_query}")
    
    def save_golden_thought(self, thought: Thought, search_results: Optional[List[SearchResult]] = None):
        """Save a golden thought to a markdown file"""
        timestamp = thought.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"golden_thought_{timestamp}.md"

        with open(filename, 'w') as f:
            f.write(f"# Golden Thought - {thought.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Interest Score:** {thought.interest_score:.2f}\n\n")
            f.write(f"**Type:** {thought.thought_type.replace('_', ' ').title()}\n\n")

            if thought.search_query:
                f.write(f"**Search Query:** {thought.search_query}\n\n")
                if search_results:
                    f.write(f"**Search Results:**\n")
                    for i, result in enumerate(search_results, 1):
                        f.write(f"{i}. [{result.title}]({result.url})\n")
                        f.write(f"   - {result.snippet}\n")
                        f.write(f"   - Source: {result.source}\n\n")

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
            model=self.config.get('model', 'gemma2:2b'),
            enable_web_search=self.config.get('enable_web_search', True),
            db_path=self.config.get('db_path', 'dreaming_memory.db')
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
            "enable_web_search": True,
            "search_cache_duration_hours": 24,
            "reasoning_strategies": {
                "free_association": 0.25,
                "logical_deduction": 0.15,
                "creative_what_if": 0.2,
                "pattern_recognition": 0.15,
                "analogical_reasoning": 0.15,
                "curiosity_driven_search": 0.10
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
                new_content, search_query, search_results = self.reasoning_engine.generate_thought(context)

                if new_content:
                    # Determine thought type based on whether search was performed
                    thought_type = 'web_search' if search_query and search_results else 'reasoning'

                    # Create thought object
                    new_thought = Thought(
                        id=f"thought_{int(time.time() * 1000)}_{thought_count}",
                        timestamp=datetime.now(),
                        content=new_content,
                        thought_type=thought_type,
                        parent_id=context[-1].id if context else None,
                        search_query=search_query
                    )

                    self._process_thought(new_thought, search_results)
                    thought_count += 1

                # Wait before next thought
                time.sleep(self.config.get('dream_interval', 5))

            except Exception as e:
                logging.error(f"Error in dream loop: {e}")
                time.sleep(1)
    
    def _process_thought(self, thought: Thought, search_results: Optional[List[SearchResult]] = None):
        """Process a single thought - analyze, store, and display"""
        # Calculate interest score
        thought.interest_score = self.interest_detector.calculate_interest_score(thought.content)

        # Boost interest score if thought involved web search
        if search_results:
            thought.interest_score = min(thought.interest_score + 0.2, 1.0)

        # Check if it's a gold strike
        if self.interest_detector.is_gold_strike(thought.content, thought.interest_score):
            thought.thought_type = 'gold_strike'
            self.memory.add_golden_thought(thought, "Autonomous discovery during dreaming")
            self.output_manager.save_golden_thought(thought, search_results)

        # Store in memory
        self.memory.add_thought(thought)
        self.thoughts_generated.append(thought)

        # Display thought
        self.output_manager.display_thought(thought, search_results)
    
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


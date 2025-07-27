#!/usr/bin/env python3
"""
Web Search Agent - Adds web search capabilities to the thinking system
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Represents a web search result"""
    title: str
    url: str
    snippet: str
    timestamp: datetime


class WebSearchAgent:
    """Agent that can perform web searches and integrate findings"""
    
    def __init__(self, search_engine: str = "duckduckgo"):
        self.search_engine = search_engine
        self.search_history = []
        self.max_results = 5
        
    def search(self, query: str) -> List[SearchResult]:
        """Perform web search (mock implementation for demo)"""
        # In a real implementation, you would integrate with:
        # - DuckDuckGo API
        # - SearxNG instance
        # - Custom search service
        
        # Mock search results for demonstration
        mock_results = [
            SearchResult(
                title=f"Search result for: {query}",
                url=f"https://example.com/search/{query.replace(' ', '-')}",
                snippet=f"This is a mock search result for the query '{query}'. In a real implementation, this would contain actual web search results.",
                timestamp=datetime.now()
            ),
            SearchResult(
                title=f"Related topic: {query}",
                url=f"https://example.com/topic/{query.replace(' ', '-')}",
                snippet=f"Additional information about {query} from web sources. This demonstrates how search results would be integrated into the thinking process.",
                timestamp=datetime.now()
            )
        ]
        
        self.search_history.append({
            'query': query,
            'timestamp': datetime.now(),
            'result_count': len(mock_results)
        })
        
        return mock_results
    
    def generate_search_query(self, context: str, api_url: str = "http://localhost:11434") -> str:
        """Generate a search query based on current thinking context"""
        prompt = f"""Based on this thinking context, generate a focused web search query to find relevant information:

Context: {context}

Generate a search query (just the query, no explanation):"""
        
        try:
            # LM Studio uses OpenAI-compatible API format
            response = requests.post(
                f"{api_url}/chat/completions",
                json={
                    "model": "gemma2:2b",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 50,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                query = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                # Clean up the query
                query = query.replace('"', '').replace("Query:", "").strip()
                return query if query else context.split('.')[0]  # Fallback
            else:
                return context.split('.')[0]  # Fallback to first sentence
                
        except Exception as e:
            print(f"Error generating search query: {e}")
            return context.split('.')[0]  # Fallback
    
    def integrate_search_results(self, original_thought: str, search_results: List[SearchResult], 
                                api_url: str = "http://localhost:11434") -> str:
        """Integrate search results with original thought"""
        if not search_results:
            return original_thought
        
        # Prepare search context
        search_context = "\n".join([
            f"- {result.title}: {result.snippet}" 
            for result in search_results[:3]  # Use top 3 results
        ])
        
        prompt = f"""Original thought: {original_thought}

Web search results:
{search_context}

Integrate the search results with the original thought to create an enhanced, more informed perspective:"""
        
        try:
            # LM Studio uses OpenAI-compatible API format
            response = requests.post(
                f"{api_url}/chat/completions",
                json={
                    "model": "gemma2:2b",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 200,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced_thought = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                return enhanced_thought if enhanced_thought else original_thought
            else:
                return original_thought
                
        except Exception as e:
            print(f"Error integrating search results: {e}")
            return original_thought


class EnhancedThoughtSeeder:
    """Enhanced thought seeder with web search capabilities"""
    
    def __init__(self, web_search_agent: WebSearchAgent):
        self.web_search_agent = web_search_agent
        self.current_topics = [
            "artificial intelligence breakthroughs 2024",
            "consciousness and AI systems",
            "quantum computing advances",
            "climate change solutions",
            "space exploration discoveries",
            "neuroscience recent findings",
            "renewable energy innovations",
            "philosophical questions about reality",
            "mathematical unsolved problems",
            "technological singularity theories"
        ]
        
    def generate_web_informed_seed(self, api_url: str = "http://localhost:11434") -> str:
        """Generate a thought seed informed by current web information"""
        import random
        
        # Select a topic to explore
        topic = random.choice(self.current_topics)
        
        # Search for current information
        search_results = self.web_search_agent.search(topic)
        
        if not search_results:
            return f"I'm curious about {topic} and what new developments might exist."
        
        # Create an informed seed thought
        result_snippet = search_results[0].snippet if search_results else ""
        
        seed_prompt = f"""Based on this current information about {topic}:

{result_snippet}

Generate a thoughtful, curious starting point for autonomous reasoning:"""
        
        try:
            # LM Studio uses OpenAI-compatible API format
            response = requests.post(
                f"{api_url}/chat/completions",
                json={
                    "model": "gemma2:2b",
                    "messages": [
                        {"role": "user", "content": seed_prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 100,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                seed = result.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
                return seed if seed else f"Current developments in {topic} make me wonder..."
            else:
                return f"What are the latest insights about {topic}?"
                
        except Exception as e:
            print(f"Error generating web-informed seed: {e}")
            return f"I'm curious about recent developments in {topic}."


def main():
    """Demo of web search integration"""
    print("🔍 Web Search Agent Demo")
    print("=" * 40)
    
    # Initialize components
    web_agent = WebSearchAgent()
    enhanced_seeder = EnhancedThoughtSeeder(web_agent)
    
    # Generate web-informed seed
    print("Generating web-informed thought seed...")
    seed = enhanced_seeder.generate_web_informed_seed()
    print(f"Seed: {seed}")
    
    # Demonstrate search integration
    print(f"\nGenerating search query from seed...")
    query = web_agent.generate_search_query(seed)
    print(f"Search query: {query}")
    
    print(f"\nPerforming search...")
    results = web_agent.search(query)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result.title}")
        print(f"   {result.snippet[:100]}...")
    
    print(f"\nIntegrating search results with original thought...")
    enhanced = web_agent.integrate_search_results(seed, results)
    print(f"Enhanced thought: {enhanced}")


if __name__ == "__main__":
    main()
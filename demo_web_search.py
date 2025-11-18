#!/usr/bin/env python3
"""
DreamingAI Web Search Demo

This script demonstrates the web search integration capabilities
without requiring a full dreaming session or Ollama installation.
Perfect for showcasing the features and understanding how they work.
"""

import time
from datetime import datetime
from dreaming_ai import (
    WebSearchEngine,
    CuriosityDetector,
    SearchCache,
    Thought
)


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_section(text: str):
    """Print a section divider"""
    print("\n" + "-" * 70)
    print(text)
    print("-" * 70 + "\n")


def demo_curiosity_detection():
    """Demonstrate the curiosity detection system"""
    print_header("DEMO 1: CURIOSITY DETECTION")

    detector = CuriosityDetector()

    example_thoughts = [
        "I notice the sky has interesting patterns today.",
        "What is the nature of consciousness?",
        "The neural networks seem to work through backpropagation.",
        "How do black holes form?",
        "I wonder about the origins of language",
        "Who discovered penicillin?",
        "This is fascinating but I'm not sure why.",
        "When did humans first use fire?",
    ]

    print("Testing various thoughts for curiosity...\n")

    for thought in example_thoughts:
        is_curious, query = detector.detect_curiosity(thought)

        # Format output
        status = "🔍 CURIOUS" if is_curious else "💭 NORMAL "

        print(f"{status} | \"{thought}\"")

        if is_curious and query:
            print(f"         └─ Extracted query: \"{query}\"")

        time.sleep(0.3)  # For dramatic effect

    print("\n✓ Curiosity detection identifies when AI wants to learn more!")


def demo_web_search():
    """Demonstrate actual web searching"""
    print_header("DEMO 2: WEB SEARCH IN ACTION")

    search_engine = WebSearchEngine(cache_duration_hours=1)

    test_queries = [
        ("artificial intelligence", "auto"),
        ("quantum mechanics", "wikipedia"),
        ("Python programming", "duckduckgo"),
    ]

    for query, source in test_queries:
        print_section(f"Searching for: \"{query}\" (source: {source})")

        try:
            results = search_engine.search(query, max_results=3, prefer_source=source)

            if results:
                print(f"✓ Found {len(results)} results:\n")

                for i, result in enumerate(results, 1):
                    print(f"{i}. {result.title}")
                    print(f"   Source: {result.source}")
                    print(f"   URL: {result.url}")
                    print(f"   Snippet: {result.snippet[:150]}...")
                    print()

                # Demonstrate caching
                print("Testing cache retrieval...")
                time.sleep(0.5)

                cached_results = search_engine.cache.get(query)
                if cached_results:
                    print(f"✓ Results successfully cached! ({len(cached_results)} results)")
                else:
                    print("⚠ Cache miss (unexpected)")

            else:
                print("⚠ No results found (possible network issue)")

        except Exception as e:
            print(f"✗ Error during search: {e}")

        time.sleep(2)  # Be nice to the APIs

    print("\n✓ Web search can find information from multiple sources!")


def demo_search_flow():
    """Demonstrate the complete search flow"""
    print_header("DEMO 3: COMPLETE SEARCH FLOW")

    print("Simulating an AI thought that triggers a search...\n")

    # Simulate a curious thought
    thought_content = "I'm curious about how photosynthesis works at the molecular level"

    print(f"💭 AI Thought: \"{thought_content}\"\n")

    # Step 1: Detect curiosity
    print("Step 1: Detecting curiosity...")
    detector = CuriosityDetector()
    is_curious, query = detector.detect_curiosity(thought_content)

    if is_curious:
        print(f"✓ Curiosity detected!")
        print(f"✓ Extracted query: \"{query}\"\n")
    else:
        print("✗ No curiosity detected (unexpected)")
        return

    # Step 2: Check cache
    print("Step 2: Checking cache...")
    cache = SearchCache()
    cached_results = cache.get(query)

    if cached_results:
        print(f"✓ Found cached results! ({len(cached_results)} results)")
        results = cached_results
    else:
        print("✗ Cache miss, performing web search...\n")

        # Step 3: Perform search
        print("Step 3: Searching the web...")
        search_engine = WebSearchEngine()

        try:
            results = search_engine.search(query, max_results=3)

            if results:
                print(f"✓ Found {len(results)} results!\n")
            else:
                print("⚠ No results found")
                return

        except Exception as e:
            print(f"✗ Search failed: {e}")
            return

    # Step 4: Display results
    print("Step 4: Processing search results...")
    print("\n📚 Search Results:\n")

    for i, result in enumerate(results[:3], 1):
        print(f"{i}. {result.title}")
        print(f"   {result.snippet[:120]}...")
        print()

    # Step 5: Simulate integration into reasoning
    print("Step 5: Integrating into reasoning...")
    print("\n💡 AI Reflection:")
    print("   'Based on what I learned about photosynthesis, it involves")
    print("   complex molecular processes where chlorophyll captures light")
    print("   energy and converts it into chemical energy. This is a")
    print("   fascinating example of biological efficiency!'\n")

    print("✓ Complete search flow executed successfully!")


def demo_analytics_preview():
    """Preview analytics capabilities"""
    print_header("DEMO 4: ANALYTICS PREVIEW")

    print("The search analytics module can track:\n")

    features = [
        "📊 Total searches and unique queries",
        "📈 Search rate and frequency patterns",
        "🎯 Most curious topics",
        "⭐ High-value search-driven insights",
        "🔍 Search source distribution",
        "📅 Search timeline and trends",
        "💎 Golden thoughts from searches",
    ]

    for feature in features:
        print(f"  {feature}")
        time.sleep(0.2)

    print("\n✓ Run 'python3 search_analytics.py' to see detailed analytics!")


def demo_integration_benefits():
    """Show the benefits of web search integration"""
    print_header("BENEFITS OF WEB SEARCH INTEGRATION")

    benefits = [
        ("🧠 Enhanced Learning", "AI can fact-check and expand its knowledge autonomously"),
        ("🔬 Grounded Thinking", "Connects abstract thoughts to real-world information"),
        ("💡 Better Insights", "More informed reasoning leads to higher-quality discoveries"),
        ("🌐 Current Information", "Access to up-to-date knowledge from Wikipedia and DuckDuckGo"),
        ("🚀 Autonomous Growth", "No human intervention needed for learning"),
        ("📊 Trackable Curiosity", "Full visibility into what AI searches and learns"),
    ]

    for title, description in benefits:
        print(f"{title}")
        print(f"  └─ {description}\n")
        time.sleep(0.3)


def main():
    """Run the complete demo"""
    print("\n" + "=" * 70)
    print("🌟 DREAMING AI - WEB SEARCH INTEGRATION DEMO 🌟".center(70))
    print("=" * 70)
    print("\nThis demo showcases the autonomous curiosity-driven web search")
    print("capabilities integrated into the DreamingAI reasoning system.\n")

    input("Press Enter to start the demo...")

    # Run all demos
    demo_curiosity_detection()
    input("\nPress Enter to continue to the next demo...")

    # Check if user wants to run web search (requires internet)
    print_section("NETWORK REQUIRED FOR NEXT DEMOS")
    response = input("The next demos require internet access. Continue? (y/n): ")

    if response.lower() in ['y', 'yes']:
        demo_web_search()
        input("\nPress Enter to continue...")

        demo_search_flow()
        input("\nPress Enter to continue...")
    else:
        print("\n⚠ Skipping network-dependent demos")

    demo_analytics_preview()
    input("\nPress Enter to continue...")

    demo_integration_benefits()

    # Final summary
    print_header("DEMO COMPLETE!")

    print("This demo showcased:")
    print("  ✓ Automatic curiosity detection")
    print("  ✓ Multi-backend web searching")
    print("  ✓ Intelligent caching")
    print("  ✓ Complete search flow")
    print("  ✓ Analytics capabilities")
    print("  ✓ Integration benefits\n")

    print("To use these features in DreamingAI:")
    print("  1. Ensure 'enable_web_search: true' in config.json")
    print("  2. Run: python3 dreaming_ai.py")
    print("  3. Choose 'start' to begin a dreaming session")
    print("  4. Watch as the AI autonomously searches when curious!\n")

    print("For analytics:")
    print("  Run: python3 search_analytics.py\n")

    print("Documentation:")
    print("  See WEB_SEARCH_IMPLEMENTATION.md for technical details\n")

    print("=" * 70)
    print("\nThank you for exploring DreamingAI's web search capabilities! 🚀\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Demo interrupted by user\n")
    except Exception as e:
        print(f"\n\n✗ Demo error: {e}\n")

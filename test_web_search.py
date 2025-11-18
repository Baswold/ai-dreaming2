#!/usr/bin/env python3
"""
Test script for DreamingAI web search functionality

This script tests the web search integration without requiring Ollama to be running.
It directly tests the WebSearchEngine, CuriosityDetector, and SearchCache components.
"""

import sys
import time
from datetime import datetime

# Test imports
try:
    from dreaming_ai import (
        WebSearchEngine,
        CuriosityDetector,
        SearchCache,
        SearchResult
    )
    print("✓ Successfully imported DreamingAI components\n")
except ImportError as e:
    print(f"✗ Failed to import components: {e}")
    sys.exit(1)


def test_curiosity_detector():
    """Test the curiosity detection system"""
    print("=" * 60)
    print("Testing Curiosity Detector")
    print("=" * 60)

    detector = CuriosityDetector()

    test_cases = [
        ("What is quantum entanglement?", True),
        ("I wonder about the history of consciousness", True),
        ("How does photosynthesis work?", True),
        ("This is just a regular thought", False),
        ("Tell me about artificial intelligence", True),
        ("The sky is blue today", False),
        ("Who invented the transistor?", True),
        ("When did the Renaissance begin?", True),
    ]

    passed = 0
    failed = 0

    for thought, expected_curious in test_cases:
        is_curious, query = detector.detect_curiosity(thought)

        if is_curious == expected_curious:
            status = "✓"
            passed += 1
        else:
            status = "✗"
            failed += 1

        print(f"\n{status} Thought: \"{thought}\"")
        print(f"  Expected curiosity: {expected_curious}")
        print(f"  Detected curiosity: {is_curious}")
        if query:
            print(f"  Extracted query: \"{query}\"")

    print(f"\n{'=' * 60}")
    print(f"Curiosity Detector Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")

    return passed, failed


def test_search_cache():
    """Test the search result caching system"""
    print("=" * 60)
    print("Testing Search Cache")
    print("=" * 60)

    cache = SearchCache(cache_duration_hours=24, db_path="test_cache.db")

    # Create test results
    test_query = "test query about AI"
    test_results = [
        SearchResult(
            title="Test Result 1",
            snippet="This is a test snippet about AI",
            url="https://example.com/1",
            source="test",
            timestamp=datetime.now()
        ),
        SearchResult(
            title="Test Result 2",
            snippet="Another test snippet",
            url="https://example.com/2",
            source="test",
            timestamp=datetime.now()
        )
    ]

    # Test cache set
    print(f"\n✓ Caching {len(test_results)} results for query: \"{test_query}\"")
    cache.set(test_query, test_results, source="test")

    # Test cache retrieval
    cached_results = cache.get(test_query)

    if cached_results and len(cached_results) == len(test_results):
        print(f"✓ Successfully retrieved {len(cached_results)} cached results")
        for i, result in enumerate(cached_results, 1):
            print(f"  {i}. {result.title} - {result.url}")
    else:
        print("✗ Failed to retrieve cached results")
        return 0, 1

    # Test cache miss
    cached_results = cache.get("non-existent query")
    if cached_results is None:
        print("✓ Cache correctly returns None for non-existent query")
    else:
        print("✗ Cache should return None for non-existent query")
        return 1, 1

    print(f"\n{'=' * 60}")
    print(f"Search Cache Results: All tests passed")
    print(f"{'=' * 60}\n")

    return 2, 0


def test_web_search():
    """Test the web search functionality"""
    print("=" * 60)
    print("Testing Web Search Engine")
    print("=" * 60)
    print("\nThis test will make actual web requests...")
    print("Testing Wikipedia search...\n")

    search_engine = WebSearchEngine(cache_duration_hours=1, db_path="test_cache.db")

    # Test Wikipedia search
    test_queries = [
        ("quantum mechanics", "wikipedia"),
        ("artificial intelligence", "auto"),
    ]

    passed = 0
    failed = 0

    for query, prefer_source in test_queries:
        print(f"\nSearching for: \"{query}\" (source: {prefer_source})")
        try:
            results = search_engine.search(query, max_results=3, prefer_source=prefer_source)

            if results:
                print(f"✓ Found {len(results)} results:")
                for i, result in enumerate(results, 1):
                    print(f"\n  {i}. {result.title}")
                    print(f"     Source: {result.source}")
                    print(f"     URL: {result.url}")
                    print(f"     Snippet: {result.snippet[:100]}...")
                passed += 1
            else:
                print(f"✗ No results found (this might be due to network issues)")
                failed += 1

            # Wait a bit between requests to be nice
            time.sleep(2)

        except Exception as e:
            print(f"✗ Error during search: {e}")
            failed += 1

    print(f"\n{'=' * 60}")
    print(f"Web Search Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")

    return passed, failed


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DreamingAI Web Search Integration Test Suite")
    print("=" * 60 + "\n")

    total_passed = 0
    total_failed = 0

    # Run tests
    print("\n>>> Test 1: Curiosity Detection\n")
    p, f = test_curiosity_detector()
    total_passed += p
    total_failed += f

    print("\n>>> Test 2: Search Cache\n")
    p, f = test_search_cache()
    total_passed += p
    total_failed += f

    print("\n>>> Test 3: Web Search (Requires Internet)\n")
    response = input("Run web search tests? This will make actual web requests (y/n): ")
    if response.lower() in ['y', 'yes']:
        p, f = test_web_search()
        total_passed += p
        total_failed += f
    else:
        print("Skipping web search tests\n")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests passed: {total_passed}")
    print(f"Total tests failed: {total_failed}")
    print(f"Success rate: {total_passed / (total_passed + total_failed) * 100:.1f}%")
    print("=" * 60 + "\n")

    if total_failed == 0:
        print("✓ All tests passed! Web search integration is working correctly.\n")
        return 0
    else:
        print(f"✗ {total_failed} tests failed. Please review the output above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Search Analytics Module for DreamingAI

This module provides tools to analyze web search behavior, identify patterns,
and generate insights about the AI's curiosity and learning patterns.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from collections import Counter, defaultdict


class SearchAnalytics:
    """Analyzes search patterns and provides insights into AI curiosity"""

    def __init__(self, db_path: str = "dreaming_memory.db"):
        self.db_path = db_path

    def get_search_statistics(self) -> Dict:
        """Get comprehensive search statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Total searches
        cursor.execute("SELECT COUNT(*) FROM thoughts WHERE search_query IS NOT NULL")
        stats['total_searches'] = cursor.fetchone()[0]

        # Unique queries
        cursor.execute("SELECT COUNT(DISTINCT search_query) FROM thoughts WHERE search_query IS NOT NULL")
        stats['unique_queries'] = cursor.fetchone()[0]

        # Total thoughts
        cursor.execute("SELECT COUNT(*) FROM thoughts")
        stats['total_thoughts'] = cursor.fetchone()[0]

        # Search rate
        if stats['total_thoughts'] > 0:
            stats['search_rate'] = stats['total_searches'] / stats['total_thoughts'] * 100
        else:
            stats['search_rate'] = 0

        # Average interest score for search-based thoughts
        cursor.execute("""
            SELECT AVG(interest_score)
            FROM thoughts
            WHERE search_query IS NOT NULL
        """)
        result = cursor.fetchone()[0]
        stats['avg_search_interest_score'] = result if result else 0

        # Golden thoughts from searches
        cursor.execute("""
            SELECT COUNT(*)
            FROM thoughts
            WHERE thought_type = 'gold_strike' AND search_query IS NOT NULL
        """)
        stats['golden_searches'] = cursor.fetchone()[0]

        # Cache statistics
        cursor.execute("SELECT COUNT(*) FROM search_cache")
        stats['cached_queries'] = cursor.fetchone()[0]

        conn.close()
        return stats

    def get_most_frequent_queries(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get the most frequently searched queries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT search_query, COUNT(*) as count
            FROM thoughts
            WHERE search_query IS NOT NULL
            GROUP BY search_query
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        conn.close()
        return results

    def get_search_timeline(self, days: int = 7) -> Dict[str, int]:
        """Get search activity over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM thoughts
            WHERE search_query IS NOT NULL AND timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (cutoff_date,))

        results = cursor.fetchall()
        conn.close()

        return {date: count for date, count in results}

    def get_curiosity_topics(self) -> Dict[str, List[str]]:
        """Analyze what topics the AI is most curious about"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT search_query
            FROM thoughts
            WHERE search_query IS NOT NULL
        """)

        queries = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Categorize queries by common words
        topic_queries = defaultdict(list)

        # Common topic indicators
        topics = {
            'science': ['physics', 'chemistry', 'biology', 'quantum', 'theory', 'scientific'],
            'philosophy': ['consciousness', 'existence', 'meaning', 'truth', 'philosophy'],
            'technology': ['computer', 'ai', 'artificial', 'intelligence', 'technology', 'algorithm'],
            'history': ['history', 'ancient', 'historical', 'civilization', 'era'],
            'mathematics': ['math', 'number', 'equation', 'theorem', 'mathematical'],
            'nature': ['nature', 'animal', 'plant', 'biology', 'ecology', 'evolution'],
            'psychology': ['mind', 'brain', 'psychology', 'behavior', 'cognitive'],
            'arts': ['art', 'music', 'literature', 'creative', 'artistic'],
        }

        for query in queries:
            query_lower = query.lower()
            categorized = False

            for topic, keywords in topics.items():
                if any(keyword in query_lower for keyword in keywords):
                    topic_queries[topic].append(query)
                    categorized = True
                    break

            if not categorized:
                topic_queries['other'].append(query)

        return dict(topic_queries)

    def get_search_source_distribution(self) -> Dict[str, int]:
        """Analyze which search sources are used most"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT source, COUNT(*) as count
            FROM search_cache
            GROUP BY source
        """)

        results = cursor.fetchall()
        conn.close()

        return {source: count for source, count in results}

    def get_high_value_searches(self, min_score: float = 0.6) -> List[Dict]:
        """Get searches that led to high-interest thoughts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT search_query, content, interest_score, timestamp
            FROM thoughts
            WHERE search_query IS NOT NULL AND interest_score >= ?
            ORDER BY interest_score DESC
        """, (min_score,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'query': row[0],
                'content': row[1][:200] + '...' if len(row[1]) > 200 else row[1],
                'score': row[2],
                'timestamp': row[3]
            })

        conn.close()
        return results

    def generate_report(self) -> str:
        """Generate a comprehensive analytics report"""
        stats = self.get_search_statistics()
        freq_queries = self.get_most_frequent_queries(5)
        topics = self.get_curiosity_topics()
        sources = self.get_search_source_distribution()
        high_value = self.get_high_value_searches(0.6)

        report = []
        report.append("=" * 70)
        report.append("DREAMING AI - SEARCH ANALYTICS REPORT")
        report.append("=" * 70)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Overall Statistics
        report.append("OVERALL STATISTICS")
        report.append("-" * 70)
        report.append(f"Total Searches:        {stats['total_searches']}")
        report.append(f"Unique Queries:        {stats['unique_queries']}")
        report.append(f"Total Thoughts:        {stats['total_thoughts']}")
        report.append(f"Search Rate:           {stats['search_rate']:.1f}%")
        report.append(f"Avg Search Interest:   {stats['avg_search_interest_score']:.2f}")
        report.append(f"Golden Searches:       {stats['golden_searches']}")
        report.append(f"Cached Queries:        {stats['cached_queries']}\n")

        # Most Frequent Queries
        report.append("TOP QUERIES")
        report.append("-" * 70)
        if freq_queries:
            for i, (query, count) in enumerate(freq_queries, 1):
                report.append(f"{i}. \"{query}\" ({count} times)")
        else:
            report.append("No queries yet")
        report.append("")

        # Curiosity Topics
        report.append("CURIOSITY BY TOPIC")
        report.append("-" * 70)
        sorted_topics = sorted(topics.items(), key=lambda x: len(x[1]), reverse=True)
        for topic, queries in sorted_topics[:8]:
            if queries:
                report.append(f"{topic.capitalize()}: {len(queries)} queries")
        report.append("")

        # Search Sources
        report.append("SEARCH SOURCE DISTRIBUTION")
        report.append("-" * 70)
        if sources:
            total_sources = sum(sources.values())
            for source, count in sources.items():
                percentage = count / total_sources * 100
                report.append(f"{source.capitalize()}: {count} ({percentage:.1f}%)")
        else:
            report.append("No search sources used yet")
        report.append("")

        # High-Value Searches
        report.append("HIGH-VALUE SEARCH-DRIVEN INSIGHTS")
        report.append("-" * 70)
        if high_value:
            for i, search in enumerate(high_value[:5], 1):
                report.append(f"\n{i}. Query: \"{search['query']}\" (Score: {search['score']:.2f})")
                report.append(f"   {search['content']}")
                report.append(f"   Time: {search['timestamp']}")
        else:
            report.append("No high-value searches yet")
        report.append("")

        report.append("=" * 70)

        return "\n".join(report)

    def export_to_json(self, output_file: str = "search_analytics.json"):
        """Export analytics data to JSON format"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'statistics': self.get_search_statistics(),
            'top_queries': [{'query': q, 'count': c} for q, c in self.get_most_frequent_queries(20)],
            'curiosity_topics': self.get_curiosity_topics(),
            'search_sources': self.get_search_source_distribution(),
            'high_value_searches': self.get_high_value_searches(0.5)
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        return output_file


def main():
    """Run analytics and generate report"""
    print("\n🔍 DreamingAI Search Analytics\n")

    analytics = SearchAnalytics()

    # Generate and display report
    report = analytics.generate_report()
    print(report)

    # Export to JSON
    json_file = analytics.export_to_json()
    print(f"\n✓ Analytics exported to: {json_file}\n")


if __name__ == "__main__":
    main()

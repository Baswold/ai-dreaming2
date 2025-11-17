#!/usr/bin/env python3
"""
Thought Replay and Simulation System

This module provides tools for replaying, simulating, and analyzing
historical dreaming sessions. Useful for understanding thought patterns,
debugging, and optimizing the system.
"""

import json
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse

from dreaming_ai import (
    Thought, MemorySystem, InterestDetector, ThoughtAnalyzer,
    OutputManager, ThoughtSeeder
)


class ThoughtReplayer:
    """Replay historical thought sessions with analysis"""

    def __init__(self, db_path: str = "dreaming_memory.db"):
        self.memory = MemorySystem(db_path=db_path)
        self.detector = InterestDetector()
        self.analyzer = ThoughtAnalyzer()
        self.output = OutputManager(verbose=True)

    def list_sessions(self) -> List[Dict]:
        """List all recorded sessions"""
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, start_time, end_time, total_thoughts, golden_thoughts, avg_interest_score
            FROM sessions
            ORDER BY start_time DESC
        ''')

        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'id': row[0],
                'start_time': row[1],
                'end_time': row[2],
                'total_thoughts': row[3],
                'golden_thoughts': row[4],
                'avg_interest_score': row[5]
            })

        conn.close()
        return sessions

    def get_session_thoughts(self, session_id: str) -> List[Thought]:
        """Get all thoughts from a specific session"""
        # Sessions don't directly link to thoughts in current schema,
        # so we'll use timestamp ranges
        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        # Get session time range
        cursor.execute('SELECT start_time, end_time FROM sessions WHERE id = ?', (session_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return []

        start_time, end_time = result

        # Get thoughts in that time range
        cursor.execute('''
            SELECT id, timestamp, content, thought_type, parent_id, interest_score,
                   tags, metadata, branch_id, web_sources
            FROM thoughts
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp ASC
        ''', (start_time, end_time))

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

    def replay_session(self, session_id: str, speed: float = 1.0, pause_on_golden: bool = True):
        """Replay a session with timing simulation

        Args:
            session_id: ID of session to replay
            speed: Playback speed multiplier (1.0 = real-time, 2.0 = double speed)
            pause_on_golden: Whether to pause on golden thoughts
        """
        thoughts = self.get_session_thoughts(session_id)

        if not thoughts:
            print(f"No thoughts found for session {session_id}")
            return

        print(f"\n🎬 Replaying session {session_id}")
        print(f"Total thoughts: {len(thoughts)}")
        print(f"Playback speed: {speed}x")
        print("=" * 60)

        for i, thought in enumerate(thoughts):
            # Calculate delay
            if i > 0:
                time_diff = (thought.timestamp - thoughts[i-1].timestamp).total_seconds()
                delay = time_diff / speed
                time.sleep(min(delay, 5.0))  # Cap at 5 seconds

            # Display thought
            self.output.display_thought(thought)

            # Pause on golden thoughts
            if pause_on_golden and thought.thought_type == 'gold_strike':
                input("\n⏸️  Press Enter to continue...")

        print("\n🎬 Replay complete!")

    def analyze_session(self, session_id: str) -> Dict:
        """Perform detailed analysis of a session"""
        thoughts = self.get_session_thoughts(session_id)

        if not thoughts:
            return {}

        print(f"\n🔍 Analyzing session {session_id}")
        print("=" * 60)

        # Basic stats
        print(f"\nTotal thoughts: {len(thoughts)}")
        print(f"Duration: {thoughts[-1].timestamp - thoughts[0].timestamp}")

        # Type distribution
        type_counts = {}
        for t in thoughts:
            type_counts[t.thought_type] = type_counts.get(t.thought_type, 0) + 1

        print("\n📊 Thought Type Distribution:")
        for thought_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            percentage = (count / len(thoughts)) * 100
            print(f"  {thought_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")

        # Interest analysis
        stats = self.analyzer.analyze_interest_evolution(thoughts)
        print("\n📈 Interest Statistics:")
        print(f"  Mean score: {stats.get('mean', 0):.3f}")
        print(f"  Min score: {stats.get('min', 0):.3f}")
        print(f"  Max score: {stats.get('max', 0):.3f}")
        print(f"  Trend: {stats.get('trend', 'unknown')}")

        # Web-informed thoughts
        web_thoughts = [t for t in thoughts if t.web_sources]
        print(f"\n🌐 Web-Informed Thoughts: {len(web_thoughts)}")

        # Theme analysis
        themes = self.analyzer.extract_themes(thoughts, top_n=10)
        print("\n🎨 Top Themes:")
        for i, (theme, count) in enumerate(themes[:5], 1):
            print(f"  {i}. {theme}: {count}")

        # Clustering
        if len(thoughts) >= 5:
            clusters = self.analyzer.cluster_thoughts(thoughts, n_clusters=min(3, len(thoughts)))
            print(f"\n🗂️  Thought Clusters: {len(clusters)}")
            for cluster_id, cluster_thoughts in clusters.items():
                print(f"  Cluster {cluster_id + 1}: {len(cluster_thoughts)} thoughts")

        return {
            'total_thoughts': len(thoughts),
            'type_distribution': type_counts,
            'interest_stats': stats,
            'web_informed_count': len(web_thoughts),
            'themes': themes
        }

    def compare_sessions(self, session_id1: str, session_id2: str):
        """Compare two sessions"""
        print(f"\n⚖️  Comparing sessions {session_id1} vs {session_id2}")
        print("=" * 60)

        thoughts1 = self.get_session_thoughts(session_id1)
        thoughts2 = self.get_session_thoughts(session_id2)

        if not thoughts1 or not thoughts2:
            print("One or both sessions not found")
            return

        # Compare basic metrics
        print(f"\n📊 Basic Comparison:")
        print(f"{'Metric':<30} {'Session 1':<15} {'Session 2':<15}")
        print("-" * 60)
        print(f"{'Total thoughts':<30} {len(thoughts1):<15} {len(thoughts2):<15}")

        # Interest scores
        stats1 = self.analyzer.analyze_interest_evolution(thoughts1)
        stats2 = self.analyzer.analyze_interest_evolution(thoughts2)

        print(f"{'Avg interest score':<30} {stats1.get('mean', 0):<15.3f} {stats2.get('mean', 0):<15.3f}")

        # Golden thoughts
        golden1 = len([t for t in thoughts1 if t.thought_type == 'gold_strike'])
        golden2 = len([t for t in thoughts2 if t.thought_type == 'gold_strike'])
        print(f"{'Golden thoughts':<30} {golden1:<15} {golden2:<15}")

        # Web-informed
        web1 = len([t for t in thoughts1 if t.web_sources])
        web2 = len([t for t in thoughts2 if t.web_sources])
        print(f"{'Web-informed thoughts':<30} {web1:<15} {web2:<15}")

        # Theme comparison
        themes1 = self.analyzer.extract_themes(thoughts1, top_n=5)
        themes2 = self.analyzer.extract_themes(thoughts2, top_n=5)

        print(f"\n🎨 Top Themes Comparison:")
        print(f"{'Session 1':<30} {'Session 2':<30}")
        print("-" * 60)

        for i in range(max(len(themes1), len(themes2))):
            theme1 = f"{themes1[i][0]}: {themes1[i][1]}" if i < len(themes1) else ""
            theme2 = f"{themes2[i][0]}: {themes2[i][1]}" if i < len(themes2) else ""
            print(f"{theme1:<30} {theme2:<30}")


class ThoughtSimulator:
    """Simulate thought generation for testing and optimization"""

    def __init__(self):
        self.seeder = ThoughtSeeder()
        self.detector = InterestDetector()

    def simulate_session(self, num_thoughts: int = 50, seed_type: str = None) -> List[Thought]:
        """Simulate a thought session without LLM calls

        Useful for testing memory, interest detection, and analysis
        """
        print(f"\n🎭 Simulating session with {num_thoughts} thoughts")
        print("=" * 60)

        thoughts = []
        simulated_contents = [
            "Patterns emerge from chaos in fascinating ways",
            "What if consciousness could be transferred?",
            "The paradox of infinity reveals deep truths",
            "Perhaps the universe is a vast simulation",
            "This connection between energy and information is profound!",
            "How do patterns replicate across different scales?",
            "The nature of time might be fundamentally different",
            "Breakthrough: everything is interconnected!",
            "Simplicity often hides great complexity",
            "What if we're asking the wrong questions?",
            "Beauty emerges from mathematical relationships",
            "The key insight is about recursion and self-reference",
            "Chaos and order are two sides of the same coin",
            "This reveals the fundamental nature of emergence",
            "Perhaps meaning arises from pattern recognition"
        ]

        # Generate seed
        seed_content = self.seeder.generate_seed(seed_type=seed_type)
        seed = Thought(
            id=f"sim_thought_0",
            timestamp=datetime.now(),
            content=seed_content,
            thought_type='seed'
        )
        seed.interest_score = self.detector.calculate_interest_score(seed_content)
        thoughts.append(seed)

        # Generate subsequent thoughts
        for i in range(1, num_thoughts):
            # Pick random content
            import random
            content = random.choice(simulated_contents)

            thought = Thought(
                id=f"sim_thought_{i}",
                timestamp=datetime.now() + timedelta(seconds=i*5),
                content=content,
                thought_type='reasoning',
                parent_id=thoughts[-1].id
            )

            # Calculate interest with context
            recent_context = thoughts[-5:] if len(thoughts) >= 5 else thoughts
            thought.interest_score = self.detector.calculate_interest_score(content, recent_context)

            # Mark gold strikes
            if self.detector.is_gold_strike(content, thought.interest_score):
                thought.thought_type = 'gold_strike'

            thoughts.append(thought)

            # Occasional web-informed simulation
            if random.random() < 0.2:
                thought.web_sources = ["https://example.com/simulated"]
                thought.thought_type = 'web_search'

            # Brief delay for realism
            time.sleep(0.01)

        print(f"✅ Simulated {len(thoughts)} thoughts")
        return thoughts

    def benchmark_interest_detection(self, num_iterations: int = 1000):
        """Benchmark interest detection performance"""
        print(f"\n⏱️  Benchmarking interest detection ({num_iterations} iterations)")
        print("=" * 60)

        test_thoughts = [
            "Simple thought.",
            "What if this is a more interesting thought with questions?",
            "Breakthrough! This reveals a fundamental paradigm shift!",
            "A longer thought that explores ideas in depth with multiple connections and patterns emerging from the text.",
        ]

        import timeit

        for thought in test_thoughts:
            time_taken = timeit.timeit(
                lambda: self.detector.calculate_interest_score(thought),
                number=num_iterations
            )
            avg_time = (time_taken / num_iterations) * 1000  # ms
            print(f"\nThought: {thought[:50]}...")
            print(f"  Avg time: {avg_time:.4f} ms")
            print(f"  Score: {self.detector.calculate_interest_score(thought):.3f}")


class SessionAnalyzer:
    """Advanced session analysis and pattern detection"""

    def __init__(self, db_path: str = "dreaming_memory.db"):
        self.memory = MemorySystem(db_path=db_path)
        self.analyzer = ThoughtAnalyzer()

    def analyze_all_sessions(self):
        """Analyze patterns across all sessions"""
        print("\n🔍 Analyzing all sessions")
        print("=" * 60)

        conn = sqlite3.connect(self.memory.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*), AVG(total_thoughts), AVG(golden_thoughts), AVG(avg_interest_score)
            FROM sessions
        ''')

        count, avg_thoughts, avg_golden, avg_score = cursor.fetchone()

        print(f"\nTotal sessions: {count}")
        print(f"Avg thoughts per session: {avg_thoughts:.1f}")
        print(f"Avg golden thoughts: {avg_golden:.1f}")
        print(f"Avg interest score: {avg_score:.3f}")

        # Session length analysis
        cursor.execute('''
            SELECT start_time, end_time FROM sessions
        ''')

        durations = []
        for start, end in cursor.fetchall():
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end)
            duration = (end_dt - start_dt).total_seconds() / 60  # minutes
            durations.append(duration)

        if durations:
            print(f"\nAvg session duration: {sum(durations)/len(durations):.1f} minutes")
            print(f"Shortest session: {min(durations):.1f} minutes")
            print(f"Longest session: {max(durations):.1f} minutes")

        conn.close()

        # Analyze all thoughts
        all_thoughts = self.memory.get_all_thoughts(limit=1000)
        if all_thoughts:
            print(f"\n📊 Overall thought statistics:")
            print(f"Total thoughts in database: {len(all_thoughts)}")

            themes = self.analyzer.extract_themes(all_thoughts, top_n=10)
            print("\n🎨 Most common themes across all sessions:")
            for i, (theme, count) in enumerate(themes[:10], 1):
                print(f"  {i:2d}. {theme}: {count}")

    def find_thought_chains(self, min_chain_length: int = 5) -> List[List[Thought]]:
        """Find interesting thought chains (parent-child relationships)"""
        print(f"\n🔗 Finding thought chains (min length: {min_chain_length})")
        print("=" * 60)

        all_thoughts = self.memory.get_all_thoughts(limit=1000)

        # Build parent-child map
        children_map = {}
        thought_map = {t.id: t for t in all_thoughts}

        for thought in all_thoughts:
            if thought.parent_id:
                if thought.parent_id not in children_map:
                    children_map[thought.parent_id] = []
                children_map[thought.parent_id].append(thought)

        # Find chains
        def build_chain(thought_id):
            chain = [thought_map[thought_id]]
            while chain[-1].parent_id and chain[-1].parent_id in thought_map:
                chain.insert(0, thought_map[chain[-1].parent_id])
                if len(chain) > 100:  # Prevent infinite loops
                    break
            return chain

        chains = []
        seen = set()

        for thought in all_thoughts:
            if thought.id not in seen:
                chain = build_chain(thought.id)
                if len(chain) >= min_chain_length:
                    chains.append(chain)
                    seen.update(t.id for t in chain)

        print(f"Found {len(chains)} chains")

        # Show top chains by average interest
        if chains:
            chains.sort(key=lambda c: sum(t.interest_score for t in c) / len(c), reverse=True)

            print("\n🏆 Top 3 chains by average interest:")
            for i, chain in enumerate(chains[:3], 1):
                avg_interest = sum(t.interest_score for t in chain) / len(chain)
                print(f"\nChain {i}: {len(chain)} thoughts, avg interest: {avg_interest:.3f}")
                print(f"  Start: {chain[0].content[:60]}...")
                print(f"  End: {chain[-1].content[:60]}...")

        return chains


def main():
    """Main CLI for thought replay and simulation"""
    parser = argparse.ArgumentParser(
        description="Thought Replay and Simulation System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--list-sessions', action='store_true',
                       help='List all recorded sessions')

    parser.add_argument('--replay', type=str, metavar='SESSION_ID',
                       help='Replay a specific session')

    parser.add_argument('--speed', type=float, default=1.0,
                       help='Replay speed multiplier (default: 1.0)')

    parser.add_argument('--analyze', type=str, metavar='SESSION_ID',
                       help='Analyze a specific session')

    parser.add_argument('--compare', nargs=2, metavar=('SESSION1', 'SESSION2'),
                       help='Compare two sessions')

    parser.add_argument('--simulate', type=int, metavar='NUM_THOUGHTS',
                       help='Simulate a session with N thoughts')

    parser.add_argument('--benchmark', action='store_true',
                       help='Run performance benchmarks')

    parser.add_argument('--analyze-all', action='store_true',
                       help='Analyze all sessions')

    parser.add_argument('--find-chains', type=int, metavar='MIN_LENGTH', default=5,
                       help='Find thought chains (default min length: 5)')

    parser.add_argument('--db-path', type=str, default='dreaming_memory.db',
                       help='Path to database file')

    args = parser.parse_args()

    # Initialize components
    replayer = ThoughtReplayer(db_path=args.db_path)
    simulator = ThoughtSimulator()
    session_analyzer = SessionAnalyzer(db_path=args.db_path)

    # Execute commands
    if args.list_sessions:
        sessions = replayer.list_sessions()
        print("\n📋 Recorded Sessions:")
        print("=" * 80)
        for i, session in enumerate(sessions, 1):
            print(f"\n{i}. {session['id']}")
            print(f"   Time: {session['start_time']} - {session['end_time']}")
            print(f"   Thoughts: {session['total_thoughts']} (Golden: {session['golden_thoughts']})")
            print(f"   Avg Interest: {session['avg_interest_score']:.3f}")

    elif args.replay:
        replayer.replay_session(args.replay, speed=args.speed)

    elif args.analyze:
        replayer.analyze_session(args.analyze)

    elif args.compare:
        replayer.compare_sessions(args.compare[0], args.compare[1])

    elif args.simulate:
        thoughts = simulator.simulate_session(num_thoughts=args.simulate)
        print(f"\n✅ Generated {len(thoughts)} simulated thoughts")

    elif args.benchmark:
        simulator.benchmark_interest_detection()

    elif args.analyze_all:
        session_analyzer.analyze_all_sessions()

    elif args.find_chains:
        session_analyzer.find_thought_chains(min_chain_length=args.find_chains)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

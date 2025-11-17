#!/usr/bin/env python3
"""
Thought Graph Network Analysis

Analyzes thought relationships as a network graph, identifying:
- Central/influential thoughts
- Community clusters
- Information flow patterns
- Conceptual bridges
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, deque
import argparse

from dreaming_ai import Thought, MemorySystem

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    import numpy as np
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("⚠️  NetworkX not available. Install with: pip install networkx")


class ThoughtGraph:
    """Build and analyze thought relationship graphs"""

    def __init__(self, db_path: str = "dreaming_memory.db"):
        self.memory = MemorySystem(db_path=db_path)
        self.graph = None

        if not NETWORKX_AVAILABLE:
            print("⚠️  Graph analysis features disabled without NetworkX")

    def build_graph(self, limit: int = 1000) -> Optional[object]:
        """Build directed graph from thought relationships"""
        if not NETWORKX_AVAILABLE:
            return None

        print(f"\n🕸️  Building thought graph (limit: {limit})")
        print("=" * 60)

        thoughts = self.memory.get_all_thoughts(limit=limit)

        if not thoughts:
            print("No thoughts found")
            return None

        # Create directed graph
        G = nx.DiGraph()

        # Add nodes
        for thought in thoughts:
            G.add_node(thought.id, **{
                'content': thought.content[:100],  # Truncate for display
                'type': thought.thought_type,
                'interest_score': thought.interest_score,
                'timestamp': thought.timestamp.isoformat(),
                'web_sources': len(thought.web_sources)
            })

        # Add edges (parent -> child relationships)
        for thought in thoughts:
            if thought.parent_id and thought.parent_id in G:
                G.add_edge(thought.parent_id, thought.id, **{
                    'weight': thought.interest_score
                })

        self.graph = G

        print(f"✅ Graph built:")
        print(f"   Nodes: {G.number_of_nodes()}")
        print(f"   Edges: {G.number_of_edges()}")
        print(f"   Density: {nx.density(G):.4f}")

        return G

    def find_central_thoughts(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """Find most central/influential thoughts using various centrality measures"""
        if not self.graph or not NETWORKX_AVAILABLE:
            return []

        print(f"\n🎯 Finding top {top_n} central thoughts")
        print("=" * 60)

        results = {}

        # Degree centrality (most connected)
        print("\n📊 By Degree Centrality (most connected):")
        degree_cent = nx.degree_centrality(self.graph)
        top_degree = sorted(degree_cent.items(), key=lambda x: -x[1])[:top_n]

        for i, (node_id, score) in enumerate(top_degree, 1):
            node_data = self.graph.nodes[node_id]
            print(f"{i:2d}. Score: {score:.4f} - {node_data['content'][:60]}...")
            results[f'degree_{i}'] = (node_id, score)

        # Betweenness centrality (information brokers)
        print("\n📊 By Betweenness Centrality (information bridges):")
        try:
            between_cent = nx.betweenness_centrality(self.graph)
            top_between = sorted(between_cent.items(), key=lambda x: -x[1])[:top_n]

            for i, (node_id, score) in enumerate(top_between, 1):
                if score > 0:  # Only show non-zero
                    node_data = self.graph.nodes[node_id]
                    print(f"{i:2d}. Score: {score:.4f} - {node_data['content'][:60]}...")
        except:
            print("   (Betweenness calculation failed - graph may be disconnected)")

        # PageRank (influence propagation)
        print("\n📊 By PageRank (influence propagation):")
        try:
            pagerank = nx.pagerank(self.graph)
            top_pagerank = sorted(pagerank.items(), key=lambda x: -x[1])[:top_n]

            for i, (node_id, score) in enumerate(top_pagerank, 1):
                node_data = self.graph.nodes[node_id]
                print(f"{i:2d}. Score: {score:.6f} - {node_data['content'][:60]}...")
        except:
            print("   (PageRank calculation failed)")

        return top_degree

    def find_communities(self) -> Dict[int, List[str]]:
        """Detect communities/clusters in thought network"""
        if not self.graph or not NETWORKX_AVAILABLE:
            return {}

        print("\n👥 Detecting thought communities")
        print("=" * 60)

        # Convert to undirected for community detection
        G_undirected = self.graph.to_undirected()

        try:
            # Use Louvain method for community detection
            from networkx.algorithms import community

            communities = community.greedy_modularity_communities(G_undirected)

            print(f"\nFound {len(communities)} communities:")

            community_map = {}
            for i, comm in enumerate(communities):
                community_map[i] = list(comm)

                print(f"\nCommunity {i + 1}: {len(comm)} thoughts")

                # Show sample thoughts from community
                sample_size = min(3, len(comm))
                for node_id in list(comm)[:sample_size]:
                    node_data = self.graph.nodes[node_id]
                    print(f"  • {node_data['content'][:70]}...")

            return community_map

        except Exception as e:
            print(f"Community detection failed: {e}")
            return {}

    def find_paths(self, start_id: str, end_id: str) -> List[List[str]]:
        """Find all paths between two thoughts"""
        if not self.graph or not NETWORKX_AVAILABLE:
            return []

        try:
            # Find all simple paths (no cycles)
            paths = list(nx.all_simple_paths(self.graph, start_id, end_id, cutoff=10))

            print(f"\n🛤️  Found {len(paths)} paths from {start_id} to {end_id}")

            for i, path in enumerate(paths[:5], 1):  # Show first 5
                print(f"\nPath {i} ({len(path)} steps):")
                for node_id in path:
                    node_data = self.graph.nodes[node_id]
                    print(f"  → {node_data['content'][:60]}...")

            return paths

        except nx.NetworkXNoPath:
            print(f"No path exists between {start_id} and {end_id}")
            return []
        except Exception as e:
            print(f"Path finding failed: {e}")
            return []

    def analyze_thought_flow(self):
        """Analyze how thoughts flow and evolve"""
        if not self.graph or not NETWORKX_AVAILABLE:
            return

        print("\n🌊 Analyzing thought flow patterns")
        print("=" * 60)

        # Find seed thoughts (no parents)
        seeds = [n for n in self.graph.nodes() if self.graph.in_degree(n) == 0]
        print(f"\nSeed thoughts: {len(seeds)}")

        # Find terminal thoughts (no children)
        terminals = [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]
        print(f"Terminal thoughts: {len(terminals)}")

        # Find branching points (multiple children)
        branching = [(n, self.graph.out_degree(n))
                    for n in self.graph.nodes()
                    if self.graph.out_degree(n) > 1]

        if branching:
            branching.sort(key=lambda x: -x[1])
            print(f"\nTop branching points:")
            for node_id, degree in branching[:5]:
                node_data = self.graph.nodes[node_id]
                print(f"  {degree} branches: {node_data['content'][:60]}...")

        # Analyze longest chains
        print("\n📏 Longest thought chains:")
        try:
            longest_paths = []
            for seed in seeds[:10]:  # Check first 10 seeds
                for terminal in terminals[:10]:
                    try:
                        path = nx.shortest_path(self.graph, seed, terminal)
                        longest_paths.append(path)
                    except:
                        pass

            if longest_paths:
                longest_paths.sort(key=len, reverse=True)

                for i, path in enumerate(longest_paths[:3], 1):
                    print(f"\nChain {i}: {len(path)} thoughts")
                    print(f"  Start: {self.graph.nodes[path[0]]['content'][:50]}...")
                    print(f"  End: {self.graph.nodes[path[-1]]['content'][:50]}...")

        except Exception as e:
            print(f"  Chain analysis failed: {e}")

    def visualize_graph(self, output_file: str = "thought_graph.png",
                       highlight_golden: bool = True,
                       max_nodes: int = 100):
        """Create visualization of thought graph"""
        if not self.graph or not NETWORKX_AVAILABLE:
            print("Graph visualization not available")
            return

        print(f"\n🎨 Creating graph visualization")
        print("=" * 60)

        # Limit graph size for visualization
        if self.graph.number_of_nodes() > max_nodes:
            # Take subgraph of most central nodes
            degree_cent = nx.degree_centrality(self.graph)
            top_nodes = sorted(degree_cent.items(), key=lambda x: -x[1])[:max_nodes]
            subgraph = self.graph.subgraph([n for n, _ in top_nodes])
            print(f"Visualizing top {max_nodes} central nodes")
        else:
            subgraph = self.graph

        # Create layout
        pos = nx.spring_layout(subgraph, k=0.5, iterations=50)

        # Prepare node colors based on type
        node_colors = []
        for node in subgraph.nodes():
            node_type = subgraph.nodes[node]['type']
            if node_type == 'gold_strike':
                node_colors.append('#FFD700')  # Gold
            elif node_type == 'seed':
                node_colors.append('#90EE90')  # Light green
            elif node_type == 'web_search':
                node_colors.append('#87CEEB')  # Sky blue
            else:
                node_colors.append('#D3D3D3')  # Light gray

        # Node sizes based on interest score
        node_sizes = [
            subgraph.nodes[node]['interest_score'] * 1000 + 100
            for node in subgraph.nodes()
        ]

        # Create figure
        plt.figure(figsize=(16, 12))

        # Draw graph
        nx.draw_networkx_nodes(
            subgraph, pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.7
        )

        nx.draw_networkx_edges(
            subgraph, pos,
            edge_color='gray',
            alpha=0.3,
            arrows=True,
            arrowsize=10,
            arrowstyle='->'
        )

        # Add labels for golden thoughts if highlighting
        if highlight_golden:
            golden_nodes = {n: subgraph.nodes[n]['content'][:20] + "..."
                          for n in subgraph.nodes()
                          if subgraph.nodes[n]['type'] == 'gold_strike'}

            if golden_nodes:
                nx.draw_networkx_labels(
                    subgraph, pos,
                    golden_nodes,
                    font_size=8,
                    font_weight='bold'
                )

        plt.title("Thought Network Graph\n(Size = Interest Score, Gold = Golden Thoughts, Green = Seeds, Blue = Web-Informed)",
                 fontsize=12)
        plt.axis('off')
        plt.tight_layout()

        # Save
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved to {output_file}")

        plt.close()

    def export_graph(self, output_file: str = "thought_graph.gexf"):
        """Export graph to file format for external analysis"""
        if not self.graph or not NETWORKX_AVAILABLE:
            return

        print(f"\n💾 Exporting graph to {output_file}")

        # Determine format from extension
        if output_file.endswith('.gexf'):
            nx.write_gexf(self.graph, output_file)
        elif output_file.endswith('.graphml'):
            nx.write_graphml(self.graph, output_file)
        elif output_file.endswith('.json'):
            from networkx.readwrite import json_graph
            data = json_graph.node_link_data(self.graph)
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print(f"Unknown format. Supported: .gexf, .graphml, .json")
            return

        print(f"✅ Graph exported to {output_file}")

    def find_isolated_thoughts(self) -> List[str]:
        """Find thoughts with no connections"""
        if not self.graph:
            return []

        isolated = list(nx.isolates(self.graph))

        print(f"\n🏝️  Found {len(isolated)} isolated thoughts:")
        for node_id in isolated[:10]:
            node_data = self.graph.nodes[node_id]
            print(f"  • {node_data['content'][:70]}...")

        return isolated

    def analyze_interest_propagation(self):
        """Analyze how interest scores propagate through the graph"""
        if not self.graph or not NETWORKX_AVAILABLE:
            return

        print("\n📈 Analyzing interest score propagation")
        print("=" * 60)

        # For each node, compare its interest to its parent's interest
        increases = []
        decreases = []

        for node in self.graph.nodes():
            parents = list(self.graph.predecessors(node))
            if parents:
                node_interest = self.graph.nodes[node]['interest_score']
                parent = parents[0]  # Take first parent
                parent_interest = self.graph.nodes[parent]['interest_score']

                diff = node_interest - parent_interest

                if diff > 0:
                    increases.append((node, parent, diff))
                elif diff < 0:
                    decreases.append((node, parent, abs(diff)))

        print(f"\nInterest increases: {len(increases)}")
        print(f"Interest decreases: {len(decreases)}")

        if increases:
            increases.sort(key=lambda x: -x[2])
            print("\n🔥 Biggest interest jumps:")
            for node, parent, diff in increases[:5]:
                node_data = self.graph.nodes[node]
                print(f"  +{diff:.3f}: {node_data['content'][:60]}...")

        if decreases:
            decreases.sort(key=lambda x: -x[2])
            print("\n📉 Biggest interest drops:")
            for node, parent, diff in decreases[:5]:
                node_data = self.graph.nodes[node]
                print(f"  -{diff:.3f}: {node_data['content'][:60]}...")


class ThoughtNetworkMetrics:
    """Calculate various network metrics"""

    def __init__(self, graph):
        self.graph = graph

    def calculate_all_metrics(self) -> Dict:
        """Calculate comprehensive network metrics"""
        if not self.graph or not NETWORKX_AVAILABLE:
            return {}

        print("\n📊 Calculating network metrics")
        print("=" * 60)

        metrics = {}

        # Basic metrics
        metrics['num_nodes'] = self.graph.number_of_nodes()
        metrics['num_edges'] = self.graph.number_of_edges()
        metrics['density'] = nx.density(self.graph)

        # Connectivity
        if self.graph.number_of_nodes() > 0:
            # Use weakly connected components for directed graphs
            num_components = nx.number_weakly_connected_components(self.graph)
            metrics['num_components'] = num_components

            # Get largest component
            largest_cc = max(nx.weakly_connected_components(self.graph), key=len)
            metrics['largest_component_size'] = len(largest_cc)

        # Degree statistics
        degrees = [d for n, d in self.graph.degree()]
        if degrees:
            metrics['avg_degree'] = np.mean(degrees)
            metrics['max_degree'] = max(degrees)

        # Clustering (convert to undirected)
        try:
            G_undirected = self.graph.to_undirected()
            metrics['avg_clustering'] = nx.average_clustering(G_undirected)
        except:
            metrics['avg_clustering'] = 0.0

        # Diameter (for largest component)
        try:
            largest_cc_subgraph = self.graph.subgraph(largest_cc).to_undirected()
            if nx.is_connected(largest_cc_subgraph):
                metrics['diameter'] = nx.diameter(largest_cc_subgraph)
                metrics['avg_path_length'] = nx.average_shortest_path_length(largest_cc_subgraph)
        except:
            pass

        # Print metrics
        print("\nNetwork Metrics:")
        for key, value in metrics.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

        return metrics


def main():
    """Main CLI for thought graph analysis"""
    parser = argparse.ArgumentParser(
        description="Thought Graph Network Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--build', action='store_true',
                       help='Build thought graph from database')

    parser.add_argument('--limit', type=int, default=1000,
                       help='Limit number of thoughts to analyze')

    parser.add_argument('--central', action='store_true',
                       help='Find central thoughts')

    parser.add_argument('--communities', action='store_true',
                       help='Detect thought communities')

    parser.add_argument('--flow', action='store_true',
                       help='Analyze thought flow patterns')

    parser.add_argument('--visualize', type=str, metavar='OUTPUT_FILE',
                       help='Create graph visualization')

    parser.add_argument('--export', type=str, metavar='OUTPUT_FILE',
                       help='Export graph to file (.gexf, .graphml, .json)')

    parser.add_argument('--metrics', action='store_true',
                       help='Calculate network metrics')

    parser.add_argument('--isolated', action='store_true',
                       help='Find isolated thoughts')

    parser.add_argument('--propagation', action='store_true',
                       help='Analyze interest propagation')

    parser.add_argument('--db-path', type=str, default='dreaming_memory.db',
                       help='Path to database file')

    args = parser.parse_args()

    if not NETWORKX_AVAILABLE:
        print("⚠️  NetworkX required for graph analysis")
        print("Install with: pip install networkx matplotlib")
        return

    # Initialize
    graph_analyzer = ThoughtGraph(db_path=args.db_path)

    # Always build graph first
    graph_analyzer.build_graph(limit=args.limit)

    if not graph_analyzer.graph:
        print("Failed to build graph")
        return

    # Execute analysis
    if args.central:
        graph_analyzer.find_central_thoughts()

    if args.communities:
        graph_analyzer.find_communities()

    if args.flow:
        graph_analyzer.analyze_thought_flow()

    if args.visualize:
        graph_analyzer.visualize_graph(output_file=args.visualize)

    if args.export:
        graph_analyzer.export_graph(output_file=args.export)

    if args.metrics:
        metrics_calc = ThoughtNetworkMetrics(graph_analyzer.graph)
        metrics_calc.calculate_all_metrics()

    if args.isolated:
        graph_analyzer.find_isolated_thoughts()

    if args.propagation:
        graph_analyzer.analyze_interest_propagation()

    # If no specific analysis requested, do basic analysis
    if not any([args.central, args.communities, args.flow, args.visualize,
                args.export, args.metrics, args.isolated, args.propagation]):
        print("\nRunning basic analysis...")
        graph_analyzer.find_central_thoughts(top_n=5)
        graph_analyzer.analyze_thought_flow()


if __name__ == '__main__':
    main()

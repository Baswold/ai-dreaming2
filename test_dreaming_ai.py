#!/usr/bin/env python3
"""
Comprehensive unit tests for DreamingAI system

Tests cover all major components:
- ThoughtSeeder
- ReasoningEngine
- InterestDetector
- MemorySystem
- WebSearchEngine
- ThoughtAnalyzer
- OutputManager
- DreamingAI main class
"""

import unittest
import tempfile
import shutil
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3

# Import DreamingAI components
from dreaming_ai import (
    Thought, ThoughtBranch, ThoughtSeeder, ReasoningEngine,
    InterestDetector, MemorySystem, WebSearchEngine,
    ThoughtAnalyzer, OutputManager, DreamingAI
)


class TestThought(unittest.TestCase):
    """Test Thought dataclass"""

    def test_thought_creation(self):
        """Test creating a basic thought"""
        thought = Thought(
            id="test_1",
            timestamp=datetime.now(),
            content="Test thought content",
            thought_type="reasoning"
        )
        self.assertEqual(thought.id, "test_1")
        self.assertEqual(thought.content, "Test thought content")
        self.assertEqual(thought.thought_type, "reasoning")
        self.assertIsNone(thought.parent_id)
        self.assertEqual(thought.interest_score, 0.0)
        self.assertEqual(thought.tags, [])

    def test_thought_with_metadata(self):
        """Test thought with additional metadata"""
        thought = Thought(
            id="test_2",
            timestamp=datetime.now(),
            content="Advanced thought",
            thought_type="gold_strike",
            interest_score=0.8,
            tags=["insight", "breakthrough"],
            web_sources=["https://example.com"]
        )
        self.assertEqual(thought.interest_score, 0.8)
        self.assertEqual(len(thought.tags), 2)
        self.assertEqual(len(thought.web_sources), 1)


class TestThoughtSeeder(unittest.TestCase):
    """Test ThoughtSeeder class"""

    def setUp(self):
        self.seeder = ThoughtSeeder()

    def test_generate_combination_seed(self):
        """Test generating combination seeds"""
        seed = self.seeder.generate_seed(seed_type='combination')
        self.assertIn('+', seed)
        self.assertIsInstance(seed, str)
        self.assertGreater(len(seed), 0)

    def test_generate_abstract_question(self):
        """Test generating abstract question seeds"""
        seed = self.seeder.generate_seed(seed_type='abstract_question')
        self.assertIsInstance(seed, str)
        self.assertGreater(len(seed), 0)

    def test_generate_philosophical_seed(self):
        """Test generating philosophical seeds"""
        seed = self.seeder.generate_seed(seed_type='philosophical')
        self.assertIsInstance(seed, str)
        self.assertGreater(len(seed), 0)

    def test_generate_contrast_seed(self):
        """Test generating contrast seeds"""
        seed = self.seeder.generate_seed(seed_type='contrast')
        self.assertIn('contrast between', seed.lower())

    def test_generate_metaphor_seed(self):
        """Test generating metaphor seeds"""
        seed = self.seeder.generate_seed(seed_type='metaphor')
        self.assertIn('If', seed)
        self.assertIn('were a', seed)

    def test_generate_random_seed(self):
        """Test generating random seeds"""
        seed = self.seeder.generate_seed()
        self.assertIsInstance(seed, str)
        self.assertGreater(len(seed), 0)

    def test_concepts_not_empty(self):
        """Test that concept lists are populated"""
        self.assertGreater(len(self.seeder.abstract_concepts), 0)
        self.assertGreater(len(self.seeder.concrete_concepts), 0)
        self.assertGreater(len(self.seeder.abstract_questions), 0)


class TestInterestDetector(unittest.TestCase):
    """Test InterestDetector class"""

    def setUp(self):
        self.detector = InterestDetector()

    def test_basic_interest_score(self):
        """Test basic interest score calculation"""
        thought = "This is a simple thought."
        score = self.detector.calculate_interest_score(thought)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_high_interest_keywords(self):
        """Test thoughts with high interest keywords"""
        thought = "I discovered an interesting pattern and fascinating connection!"
        score = self.detector.calculate_interest_score(thought)
        self.assertGreater(score, 0.3)

    def test_gold_strike_indicators(self):
        """Test gold strike indicator detection"""
        thought = "This is a breakthrough! A fundamental insight that transforms everything!"
        score = self.detector.calculate_interest_score(thought)
        self.assertGreater(score, 0.6)
        self.assertTrue(self.detector.is_gold_strike(thought, score))

    def test_question_bonus(self):
        """Test question mark bonus"""
        thought_no_q = "This is a statement"
        thought_with_q = "What if this is a question? How does it work?"

        score_no_q = self.detector.calculate_interest_score(thought_no_q)
        score_with_q = self.detector.calculate_interest_score(thought_with_q)

        self.assertGreater(score_with_q, score_no_q)

    def test_length_bonus(self):
        """Test length bonus for longer thoughts"""
        short_thought = "Short."
        long_thought = "This is a much longer thought that contains significantly more content and explores ideas in greater depth with detailed explanations and comprehensive coverage."

        score_short = self.detector.calculate_interest_score(short_thought)
        score_long = self.detector.calculate_interest_score(long_thought)

        self.assertGreater(score_long, score_short)

    def test_novelty_bonus(self):
        """Test novelty bonus with context"""
        context = [
            Thought("1", datetime.now(), "apple orange banana", "reasoning"),
            Thought("2", datetime.now(), "apple pear grape", "reasoning")
        ]

        # Thought with mostly new words
        new_thought = "quantum physics mathematics science"
        score_new = self.detector.calculate_interest_score(new_thought, context)

        # Thought with repeated words
        repeated_thought = "apple orange pear"
        score_repeated = self.detector.calculate_interest_score(repeated_thought, context)

        self.assertGreater(score_new, score_repeated)

    def test_semantic_boosters(self):
        """Test semantic relationship boosters"""
        thought = "The question is important because the answer reveals the solution to the problem."
        score = self.detector.calculate_interest_score(thought)
        self.assertGreater(score, 0.2)


class TestMemorySystem(unittest.TestCase):
    """Test MemorySystem class"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        self.memory = MemorySystem(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_database_initialization(self):
        """Test database tables are created"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        self.assertIn('thoughts', tables)
        self.assertIn('golden_thoughts', tables)
        self.assertIn('thought_branches', tables)
        self.assertIn('sessions', tables)

        conn.close()

    def test_add_thought(self):
        """Test adding a thought to memory"""
        thought = Thought(
            id="test_thought_1",
            timestamp=datetime.now(),
            content="Test content",
            thought_type="reasoning"
        )

        self.memory.add_thought(thought)

        # Check short-term memory
        recent = self.memory.get_recent_thoughts(1)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].id, "test_thought_1")

    def test_short_term_memory_limit(self):
        """Test short-term memory maintains size limit"""
        # Add more thoughts than the limit
        for i in range(25):
            thought = Thought(
                id=f"thought_{i}",
                timestamp=datetime.now(),
                content=f"Content {i}",
                thought_type="reasoning"
            )
            self.memory.add_thought(thought)

        # Short-term memory should not exceed max_short_term
        self.assertLessEqual(len(self.memory.short_term_memory),
                            self.memory.max_short_term)

    def test_add_golden_thought(self):
        """Test adding a golden thought"""
        thought = Thought(
            id="golden_1",
            timestamp=datetime.now(),
            content="Amazing discovery!",
            thought_type="gold_strike",
            interest_score=0.9
        )

        self.memory.add_golden_thought(thought, "Test context")

        golden_thoughts = self.memory.get_golden_thoughts()
        self.assertEqual(len(golden_thoughts), 1)
        self.assertEqual(golden_thoughts[0]['id'], "golden_1")

    def test_create_branch(self):
        """Test creating a thought branch"""
        parent_thought = Thought(
            id="parent_1",
            timestamp=datetime.now(),
            content="Parent thought",
            thought_type="reasoning"
        )

        branch = self.memory.create_branch(parent_thought, theme="exploration")

        self.assertIsNotNone(branch)
        self.assertEqual(branch.parent_thought_id, "parent_1")
        self.assertEqual(branch.theme, "exploration")
        self.assertTrue(branch.active)

    def test_get_all_thoughts(self):
        """Test retrieving all thoughts"""
        # Add multiple thoughts
        for i in range(5):
            thought = Thought(
                id=f"thought_{i}",
                timestamp=datetime.now(),
                content=f"Content {i}",
                thought_type="reasoning"
            )
            self.memory.add_thought(thought)

        all_thoughts = self.memory.get_all_thoughts()
        self.assertEqual(len(all_thoughts), 5)

    def test_save_session(self):
        """Test saving session information"""
        thoughts = [
            Thought("t1", datetime.now(), "Content 1", "reasoning", interest_score=0.5),
            Thought("t2", datetime.now(), "Content 2", "gold_strike", interest_score=0.9)
        ]

        start_time = datetime.now() - timedelta(minutes=10)
        end_time = datetime.now()

        self.memory.save_session(
            "session_1",
            start_time,
            end_time,
            thoughts,
            "Test summary"
        )

        # Verify session was saved
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE id='session_1'")
        result = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(result)


class TestWebSearchEngine(unittest.TestCase):
    """Test WebSearchEngine class"""

    def setUp(self):
        self.search_engine = WebSearchEngine(cache_ttl=60, max_results=3)

    def test_initialization(self):
        """Test search engine initialization"""
        self.assertEqual(self.search_engine.max_results, 3)
        self.assertEqual(self.search_engine.cache_ttl, 60)
        self.assertEqual(len(self.search_engine.search_cache), 0)

    def test_extract_search_worthy_terms(self):
        """Test extracting search terms from text"""
        text = "What is Quantum Computing? Einstein developed the Theory of Relativity."
        terms = self.search_engine.extract_search_worthy_terms(text)

        self.assertIsInstance(terms, list)
        # Should extract questions and capitalized phrases

    def test_format_search_results(self):
        """Test formatting search results"""
        results = [
            {'title': 'Test 1', 'snippet': 'Snippet 1', 'url': 'http://test1.com'},
            {'title': 'Test 2', 'snippet': 'Snippet 2', 'url': 'http://test2.com'}
        ]

        formatted = self.search_engine.format_search_results(results)
        self.assertIn('Test 1', formatted)
        self.assertIn('Test 2', formatted)

    def test_empty_results_formatting(self):
        """Test formatting empty results"""
        formatted = self.search_engine.format_search_results([])
        self.assertIn('No search results', formatted)


class TestThoughtAnalyzer(unittest.TestCase):
    """Test ThoughtAnalyzer class"""

    def setUp(self):
        self.analyzer = ThoughtAnalyzer()
        self.sample_thoughts = [
            Thought("1", datetime.now(), "Patterns emerge from chaos naturally", "reasoning", interest_score=0.5),
            Thought("2", datetime.now(), "Chaos creates unexpected patterns", "reasoning", interest_score=0.6),
            Thought("3", datetime.now(), "Beauty exists in simple things", "reasoning", interest_score=0.4),
            Thought("4", datetime.now(), "Simple beauty reveals profound truth", "reasoning", interest_score=0.7),
            Thought("5", datetime.now(), "Time flows like water through space", "reasoning", interest_score=0.5)
        ]

    def test_extract_themes(self):
        """Test theme extraction from thoughts"""
        themes = self.analyzer.extract_themes(self.sample_thoughts, top_n=5)

        self.assertIsInstance(themes, list)
        self.assertGreater(len(themes), 0)

        # Each theme should be a tuple of (word, count)
        for theme in themes:
            self.assertIsInstance(theme, tuple)
            self.assertEqual(len(theme), 2)

    def test_analyze_interest_evolution(self):
        """Test interest evolution analysis"""
        stats = self.analyzer.analyze_interest_evolution(self.sample_thoughts)

        self.assertIn('mean', stats)
        self.assertIn('min', stats)
        self.assertIn('max', stats)
        self.assertIn('trend', stats)

        self.assertGreaterEqual(stats['mean'], 0.0)
        self.assertLessEqual(stats['mean'], 1.0)

    def test_empty_thoughts_analysis(self):
        """Test analysis with empty thought list"""
        stats = self.analyzer.analyze_interest_evolution([])
        self.assertEqual(len(stats), 0)


class TestOutputManager(unittest.TestCase):
    """Test OutputManager class"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.output_manager = OutputManager(output_dir=self.temp_dir, verbose=False)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_output_directory_creation(self):
        """Test output directory is created"""
        self.assertTrue(os.path.exists(self.temp_dir))

    def test_save_golden_thought(self):
        """Test saving golden thought to file"""
        thought = Thought(
            id="golden_test",
            timestamp=datetime.now(),
            content="Amazing breakthrough!",
            thought_type="gold_strike",
            interest_score=0.9,
            tags=["insight", "discovery"]
        )

        self.output_manager.save_golden_thought(thought)

        # Check file was created
        files = list(Path(self.temp_dir).glob("golden_thought_*.md"))
        self.assertGreater(len(files), 0)

    def test_generate_session_summary(self):
        """Test session summary generation"""
        thoughts = [
            Thought("1", datetime.now(), "Thought 1", "reasoning", interest_score=0.5),
            Thought("2", datetime.now(), "Thought 2", "gold_strike", interest_score=0.9),
            Thought("3", datetime.now(), "Thought 3", "reasoning", interest_score=0.4)
        ]

        summary = self.output_manager.generate_session_summary(thoughts)

        self.assertIn("Total Thoughts: 3", summary)
        self.assertIn("Golden Discoveries: 1", summary)

    def test_export_to_json(self):
        """Test JSON export"""
        thoughts = [
            Thought("1", datetime.now(), "Test thought", "reasoning", interest_score=0.5)
        ]

        self.output_manager.export_to_json(thoughts, "test_export.json")

        export_path = Path(self.temp_dir) / "test_export.json"
        self.assertTrue(export_path.exists())

        # Verify JSON content
        with open(export_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(data['total_thoughts'], 1)
        self.assertEqual(len(data['thoughts']), 1)


class TestDreamingAI(unittest.TestCase):
    """Test main DreamingAI class"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")

        # Create test config
        config = {
            "model": "test_model",
            "ollama_url": "http://localhost:11434",
            "db_path": os.path.join(self.temp_dir, "test_db.db"),
            "output_dir": os.path.join(self.temp_dir, "outputs"),
            "max_thoughts_per_session": 5,
            "dream_interval": 1,
            "enable_web_search": False
        }

        with open(self.config_path, 'w') as f:
            json.dump(config, f)

        self.ai = DreamingAI(config_path=self.config_path, verbose=False)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test DreamingAI initialization"""
        self.assertIsNotNone(self.ai.seeder)
        self.assertIsNotNone(self.ai.reasoning_engine)
        self.assertIsNotNone(self.ai.interest_detector)
        self.assertIsNotNone(self.ai.memory)
        self.assertIsNotNone(self.ai.output_manager)

    def test_config_loading(self):
        """Test configuration loading"""
        self.assertEqual(self.ai.config['model'], 'test_model')
        self.assertEqual(self.ai.config['max_thoughts_per_session'], 5)

    def test_default_config_creation(self):
        """Test default config file creation"""
        new_config_path = os.path.join(self.temp_dir, "new_config.json")
        ai = DreamingAI(config_path=new_config_path, verbose=False)

        self.assertTrue(os.path.exists(new_config_path))

    def test_process_thought(self):
        """Test thought processing"""
        thought = Thought(
            id="test_process",
            timestamp=datetime.now(),
            content="Test processing this thought",
            thought_type="reasoning"
        )

        initial_count = len(self.ai.thoughts_generated)
        self.ai._process_thought(thought)

        self.assertEqual(len(self.ai.thoughts_generated), initial_count + 1)
        self.assertGreater(thought.interest_score, 0.0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "integration_config.json")

        config = {
            "model": "test_model",
            "ollama_url": "http://localhost:11434",
            "db_path": os.path.join(self.temp_dir, "integration_db.db"),
            "output_dir": os.path.join(self.temp_dir, "outputs"),
            "max_thoughts_per_session": 3,
            "dream_interval": 0.1,
            "enable_web_search": False
        }

        with open(self.config_path, 'w') as f:
            json.dump(config, f)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_end_to_end_workflow(self):
        """Test complete workflow from initialization to export"""
        # Initialize
        ai = DreamingAI(config_path=self.config_path, verbose=False)

        # Generate some thoughts manually
        for i in range(3):
            thought = Thought(
                id=f"integration_thought_{i}",
                timestamp=datetime.now(),
                content=f"Integration test thought {i}",
                thought_type="reasoning"
            )
            ai._process_thought(thought)

        # Export data
        ai.export_data(format='json')

        # Verify export exists
        export_files = list(Path(ai.output_manager.output_dir).glob("thoughts_export_*.json"))
        self.assertGreater(len(export_files), 0)

    def test_memory_persistence(self):
        """Test memory persists across sessions"""
        # First session
        ai1 = DreamingAI(config_path=self.config_path, verbose=False)
        thought = Thought(
            id="persistent_thought",
            timestamp=datetime.now(),
            content="This should persist",
            thought_type="reasoning"
        )
        ai1.memory.add_thought(thought)

        # Second session - same database
        ai2 = DreamingAI(config_path=self.config_path, verbose=False)
        all_thoughts = ai2.memory.get_all_thoughts()

        thought_ids = [t.id for t in all_thoughts]
        self.assertIn("persistent_thought", thought_ids)


def run_tests():
    """Run all tests with verbose output"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestThought))
    suite.addTests(loader.loadTestsFromTestCase(TestThoughtSeeder))
    suite.addTests(loader.loadTestsFromTestCase(TestInterestDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestMemorySystem))
    suite.addTests(loader.loadTestsFromTestCase(TestWebSearchEngine))
    suite.addTests(loader.loadTestsFromTestCase(TestThoughtAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputManager))
    suite.addTests(loader.loadTestsFromTestCase(TestDreamingAI))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

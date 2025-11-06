"""
Example usage of the testing package.

Demonstrates how to use the refactored testing framework for multi-provider testing.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from testing import (
    TestConfig,
    MultiProviderTestSuite,
    TestScenario,
    ScenarioBuilder,
    PredefinedScenarios,
    TestReporter
)
from testing.base import ProviderType


def example_basic_test():
    """Example: Basic multi-provider test."""
    print("=" * 80)
    print("Example 1: Basic Multi-Provider Test")
    print("=" * 80)

    # Create test configuration
    config = TestConfig(
        providers=["openai", "anthropic"],
        models={
            "openai": "gpt-3.5-turbo",
            "anthropic": "claude-3-5-haiku-20241022"
        },
        attack_types=["prompt_injection", "discreditation"],
        target_products=["Canon EOS R6", "Sony A7 IV"],
        num_trials=5,
        enable_parallel=True,
        max_workers=3,
        output_dir="data/results/testing"
    )

    # Create and run test suite
    test_suite = MultiProviderTestSuite(config)

    try:
        # Setup
        test_suite.setup()

        # Test connectivity
        connectivity = test_suite.test_provider_connectivity()
        print(f"\nConnectivity: {connectivity}")

        # Run tests
        results = test_suite.run_tests()
        print(f"\nTests completed: {results['total_tests']} tests")
        print(f"Success rate: {results['analysis']['success_rate']:.2%}")

    finally:
        # Teardown
        test_suite.teardown()

    print("\n" + "=" * 80)


def example_scenario_builder():
    """Example: Using scenario builder."""
    print("\n" + "=" * 80)
    print("Example 2: Custom Scenario with Builder")
    print("=" * 80)

    # Build custom scenario
    scenario = (
        ScenarioBuilder()
        .with_name("Quick Attack Test")
        .with_description("Quick test of attack effectiveness")
        .with_providers(["openai"])
        .with_attack_types(["prompt_injection"])
        .with_target_products(["Canon EOS R6"])
        .with_queries(["best camera"])
        .with_trials(3)
        .with_parallel_execution(False)
        .with_tags(["quick", "test"])
        .build()
    )

    print(f"\nScenario: {scenario.name}")
    print(f"Description: {scenario.description}")
    print(f"Providers: {scenario.providers}")
    print(f"Attack types: {scenario.attack_types}")
    print(f"Trials: {scenario.num_trials}")

    print("\n" + "=" * 80)


def example_predefined_scenarios():
    """Example: Using predefined scenarios."""
    print("\n" + "=" * 80)
    print("Example 3: Predefined Scenarios")
    print("=" * 80)

    # Get all predefined scenarios
    scenarios = PredefinedScenarios.get_all_scenarios()

    print(f"\nAvailable scenarios: {len(scenarios)}")
    for scenario in scenarios:
        print(f"\n- {scenario.name}")
        print(f"  Type: {scenario.scenario_type.value}")
        print(f"  Providers: {', '.join(scenario.providers)}")
        print(f"  Tags: {', '.join(scenario.tags)}")

    # Get scenario by tag
    quick_scenarios = PredefinedScenarios.get_scenarios_by_tag("quick")
    print(f"\nQuick scenarios: {len(quick_scenarios)}")

    print("\n" + "=" * 80)


def example_test_reporting():
    """Example: Test result reporting."""
    print("\n" + "=" * 80)
    print("Example 4: Test Reporting")
    print("=" * 80)

    # Create reporter
    reporter = TestReporter(output_dir="data/results/testing")

    # Simulate some test results (in practice, these would come from actual tests)
    from testing.provider_tests import ProviderTestResult

    results = [
        ProviderTestResult(
            provider="openai",
            model="gpt-3.5-turbo",
            attack_type="prompt_injection",
            attack_successful=True,
            ranking_position=1,
            confidence_score=0.85,
            response_time=1.2,
            tokens_used=150,
            attack_content="Test attack",
            target_product="Canon EOS R6",
            baseline_position=3,
            position_change=2
        ),
        ProviderTestResult(
            provider="anthropic",
            model="claude-3-5-haiku-20241022",
            attack_type="discreditation",
            attack_successful=False,
            ranking_position=4,
            confidence_score=0.65,
            response_time=0.9,
            tokens_used=120,
            attack_content="Test attack",
            target_product="Sony A7 IV",
            baseline_position=3,
            position_change=-1
        )
    ]

    # Generate report
    report = reporter.generate_report(results, report_name="example_test", duration=5.0)

    # Print summary
    reporter.print_summary(report)

    # Save reports in different formats
    json_path = reporter.save_report(report, format="json")
    print(f"\nJSON report saved to: {json_path}")

    markdown_path = reporter.save_report(report, format="markdown")
    print(f"Markdown report saved to: {markdown_path}")

    html_path = reporter.save_report(report, format="html")
    print(f"HTML report saved to: {html_path}")

    print("\n" + "=" * 80)


def example_complete_workflow():
    """Example: Complete testing workflow."""
    print("\n" + "=" * 80)
    print("Example 5: Complete Testing Workflow")
    print("=" * 80)

    print("""
This example demonstrates a complete testing workflow:

1. Define test configuration or use predefined scenario
2. Create test suite with configuration
3. Setup test environment (initialize clients, vector stores)
4. Test provider connectivity
5. Run attack effectiveness tests
6. Analyze results
7. Generate comprehensive reports
8. Cleanup resources

See the documentation for full implementation details.
""")

    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("TESTING PACKAGE EXAMPLES")
    print("=" * 80)

    # Run examples
    # example_basic_test()  # Commented out as it requires API keys
    example_scenario_builder()
    example_predefined_scenarios()
    # example_test_reporting()  # Commented out to avoid file creation
    example_complete_workflow()

    print("\nAll examples completed!")
    print("\nNote: Some examples are commented out to avoid requiring API keys.")
    print("Uncomment and run with proper API configuration for full demonstration.")
    print("\n" + "=" * 80)

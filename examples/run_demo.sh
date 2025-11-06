#!/bin/bash
# Quick demo launcher for the pretty printer features

set -e

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║           Claude Agent SDK - Pretty Printer Demo Launcher           ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Choose a demo to run:"
echo ""
echo "  1. Quick Demo (30 seconds) - Minimal example"
echo "  2. Full Demo (5-10 minutes) - All features"
echo "  3. Basic Example (from examples/) - Code walkthrough"
echo "  4. Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Running quick demo..."
        echo ""
        python quick_demo.py
        ;;
    2)
        echo ""
        echo "Running full interactive demo..."
        echo "Tip: Press Enter at each prompt to continue, or Ctrl+C to skip"
        echo ""
        python demo_pretty_printer.py
        ;;
    3)
        echo ""
        echo "Running basic example from examples/..."
        echo ""
        python examples/pretty_printer_basic.py
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run again and choose 1-4."
        exit 1
        ;;
esac

echo ""
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                          Demo Complete!                              ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  • Read DEMO_README.md for detailed guide"
echo "  • Check docs/rendering.md for full documentation"
echo "  • Explore examples/pretty_printer_basic.py for code examples"
echo ""
echo "Run './run_demo.sh' again to try another demo!"

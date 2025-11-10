#!/usr/bin/env python3
"""Syntax highlighting demonstration for 500+ programming languages.

This demo showcases the SDK's syntax highlighting capabilities:
- Automatic language detection for code blocks
- Support for 500+ programming languages via Pygments
- Theme-aware semantic mapping
- Graceful fallback if Pygments not installed
- Syntax highlighting in both code blocks and tool results

The highlighter uses a modular architecture:
1. Language detection → Identifies language from code
2. Tokenization → Pygments converts code to tokens
3. Semantic mapping → Maps tokens to semantic categories
4. Styling → Applies theme colors to semantic categories

Usage:
    # Basic demo (all features)
    python examples/syntax_highlighting_demo.py

    # Specific language
    python examples/syntax_highlighting_demo.py --lang python

    # Test with all themes
    python examples/syntax_highlighting_demo.py --all-themes

    # Disable syntax highlighting (comparison)
    python examples/syntax_highlighting_demo.py --no-syntax

Prerequisites:
    pip install claude-agent-sdk[syntax]
"""

import argparse
import io
import sys

# Set up UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from claude_agent_sdk.rendering.config import RendererConfig
from claude_agent_sdk.rendering.formatters import ClaudeCodeFormatter
from claude_agent_sdk.rendering.theme import Theme
from claude_agent_sdk.types import AssistantMessage, TextBlock, ToolResultBlock

# Sample code snippets for different languages
SAMPLE_CODE = {
    "python": """def fibonacci(n):
    \"\"\"Generate Fibonacci sequence up to n terms.\"\"\"
    if n <= 0:
        return []
    elif n == 1:
        return [0]

    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

    return fib_sequence

# Example: Get first 10 Fibonacci numbers
result = fibonacci(10)
print(f"Fibonacci sequence: {result}")""",

    "javascript": """// Async function with Promise handling
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Failed to fetch user:", error);
        return null;
    }
}

// Usage with arrow function
const users = [1, 2, 3].map(id => fetchUserData(id));""",

    "typescript": """interface User {
    id: number;
    name: string;
    email: string;
    roles: Role[];
}

type Role = "admin" | "user" | "guest";

class UserService {
    private users: Map<number, User> = new Map();

    async findById(id: number): Promise<User | undefined> {
        return this.users.get(id);
    }

    async create(user: Omit<User, "id">): Promise<User> {
        const id = this.users.size + 1;
        const newUser = { ...user, id };
        this.users.set(id, newUser);
        return newUser;
    }
}""",

    "rust": """use std::collections::HashMap;

#[derive(Debug, Clone)]
struct User {
    id: u64,
    name: String,
    email: String,
}

impl User {
    fn new(id: u64, name: String, email: String) -> Self {
        User { id, name, email }
    }
}

fn main() {
    let mut users: HashMap<u64, User> = HashMap::new();

    users.insert(1, User::new(1, "Alice".to_string(), "alice@example.com".to_string()));
    users.insert(2, User::new(2, "Bob".to_string(), "bob@example.com".to_string()));

    for (id, user) in &users {
        println!("User {}: {:?}", id, user);
    }
}""",

    "go": """package main

import (
    "fmt"
    "sync"
)

type User struct {
    ID    int
    Name  string
    Email string
}

type UserService struct {
    mu    sync.RWMutex
    users map[int]User
}

func NewUserService() *UserService {
    return &UserService{
        users: make(map[int]User),
    }
}

func (s *UserService) Create(user User) error {
    s.mu.Lock()
    defer s.mu.Unlock()

    if _, exists := s.users[user.ID]; exists {
        return fmt.Errorf("user %d already exists", user.ID)
    }

    s.users[user.ID] = user
    return nil
}""",

    "java": """import java.util.*;
import java.util.stream.*;

public class UserService {
    private Map<Integer, User> users = new HashMap<>();

    public Optional<User> findById(int id) {
        return Optional.ofNullable(users.get(id));
    }

    public List<User> findByRole(String role) {
        return users.values().stream()
            .filter(user -> user.getRoles().contains(role))
            .collect(Collectors.toList());
    }

    public void create(User user) {
        if (users.containsKey(user.getId())) {
            throw new IllegalArgumentException("User already exists");
        }
        users.put(user.getId(), user);
    }
}""",

    "json": """{
  "users": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "roles": ["admin", "user"],
      "active": true,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Bob Smith",
      "email": "bob@example.com",
      "roles": ["user"],
      "active": false,
      "created_at": "2024-02-20T14:45:00Z"
    }
  ],
  "total": 2
}""",

    "yaml": """# Kubernetes Deployment Configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  labels:
    app: web
    environment: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web-container
        image: nginx:1.21
        ports:
        - containerPort: 80
        env:
        - name: ENVIRONMENT
          value: "production"
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi\"""",

    "sql": """-- User management queries
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO users (name, email) VALUES
    ('Alice Johnson', 'alice@example.com'),
    ('Bob Smith', 'bob@example.com'),
    ('Charlie Davis', 'charlie@example.com');

-- Query with JOIN and aggregation
SELECT
    u.name,
    COUNT(o.id) as order_count,
    SUM(o.total) as total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name
HAVING COUNT(o.id) > 5
ORDER BY total_spent DESC
LIMIT 10;""",

    "bash": """#!/bin/bash
# Deployment script with error handling

set -euo pipefail

ENVIRONMENT=${1:-staging}
APP_NAME="web-app"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

deploy() {
    local env=$1
    echo "Deploying $APP_NAME to $env environment..."

    # Build application
    if ! npm run build; then
        echo "Error: Build failed" >&2
        return 1
    fi

    # Run tests
    npm test || { echo "Tests failed"; return 1; }

    # Deploy
    kubectl apply -f "k8s/$env/" --record
    kubectl rollout status deployment/$APP_NAME -n $env

    echo "Deployment completed at $TIMESTAMP"
}

deploy "$ENVIRONMENT\"""",
}


def print_header(title: str, char: str = "=") -> None:
    """Print a section header."""
    width = 80
    print(f"\n{char * width}")
    print(f"  {title}")
    print(f"{char * width}\n")


def demo_language(
    language: str,
    code: str,
    theme: Theme,
    enable_syntax: bool = True,
    theme_name: str = "claude-code-default"
) -> None:
    """Demonstrate syntax highlighting for a specific language."""
    print_header(f"Language: {language.upper()} (Theme: {theme_name})", "-")

    config = RendererConfig(
        theme=theme,
        enable_syntax_highlighting=enable_syntax,
        render_level=2,  # DETAILED
    )
    formatter = ClaudeCodeFormatter(config)

    # Create a tool result containing code (common use case)
    tool_result = AssistantMessage(
        content=[
            ToolResultBlock(
                tool_use_id="demo_tool",
                content=code,
                is_error=False,
            )
        ],
        model="claude-sonnet-4-5-20250929",
    )

    # Format and display
    output = formatter.format_assistant_message(tool_result)
    print(output)

    if not enable_syntax:
        print("  [Note: Syntax highlighting disabled for comparison]\n")


def demo_all_languages(theme: Theme, enable_syntax: bool = True, theme_name: str = "claude-code-default") -> None:
    """Demonstrate syntax highlighting across multiple languages."""
    print_header("SYNTAX HIGHLIGHTING DEMO - 500+ Languages Supported", "=")

    print(f"Theme: {theme_name}")
    print(f"Syntax Highlighting: {'Enabled' if enable_syntax else 'Disabled'}")
    print(f"Languages Shown: {len(SAMPLE_CODE)}")
    print("\nThe SDK automatically detects language and applies semantic highlighting.\n")

    for language, code in SAMPLE_CODE.items():
        demo_language(language, code, theme, enable_syntax, theme_name)


def demo_comparison() -> None:
    """Side-by-side comparison with and without syntax highlighting."""
    print_header("COMPARISON: With vs Without Syntax Highlighting", "=")

    theme = Theme.claude_code_default()
    sample_lang = "python"
    sample_code = SAMPLE_CODE[sample_lang]

    print("\n1. WITH SYNTAX HIGHLIGHTING:")
    print("=" * 80)
    demo_language(sample_lang, sample_code, theme, enable_syntax=True)

    print("\n2. WITHOUT SYNTAX HIGHLIGHTING:")
    print("=" * 80)
    demo_language(sample_lang, sample_code, theme, enable_syntax=False)

    print("\nNotice the difference:")
    print("  • Keywords, strings, comments are color-coded")
    print("  • Improved readability and code structure visibility")
    print("  • Theme-aware colors that match your terminal preferences\n")


def demo_all_themes(language: str = "python") -> None:
    """Show syntax highlighting with all available themes."""
    print_header(f"SYNTAX HIGHLIGHTING ACROSS ALL THEMES ({language.upper()})", "=")

    themes = {
        "claude-code-default": Theme.claude_code_default(),
        "solarized-dark": Theme.solarized_dark(),
        "solarized-light": Theme.solarized_light(),
        "gruvbox": Theme.gruvbox(),
        "nord": Theme.nord(),
        "monochrome": Theme.monochrome(),
        "high-contrast": Theme.high_contrast(),
    }

    code = SAMPLE_CODE[language]

    for theme_name, theme in themes.items():
        demo_language(language, code, theme, enable_syntax=True, theme_name=theme_name)


def main():
    parser = argparse.ArgumentParser(
        description="Syntax highlighting demo for 500+ languages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--lang",
        type=str,
        choices=list(SAMPLE_CODE.keys()),
        help="Show only this language (e.g., python, javascript, rust)",
    )
    parser.add_argument(
        "--all-themes",
        action="store_true",
        help="Show syntax highlighting with all available themes",
    )
    parser.add_argument(
        "--no-syntax",
        action="store_true",
        help="Disable syntax highlighting (for comparison)",
    )
    parser.add_argument(
        "--comparison",
        action="store_true",
        help="Show side-by-side comparison with/without syntax highlighting",
    )
    args = parser.parse_args()

    try:
        # Check if Pygments is available
        import pygments
        print("✓ Pygments installed - Full syntax highlighting available\n")
    except ImportError:
        print("⚠ Pygments not installed - Install with: pip install claude-agent-sdk[syntax]")
        print("  Continuing with graceful fallback...\n")

    if args.comparison:
        demo_comparison()
    elif args.all_themes:
        demo_all_themes(args.lang or "python")
    elif args.lang:
        theme = Theme.claude_code_default()
        demo_language(args.lang, SAMPLE_CODE[args.lang], theme, not args.no_syntax)
    else:
        theme = Theme.claude_code_default()
        demo_all_languages(theme, not args.no_syntax)

    # Summary
    print_header("SYNTAX HIGHLIGHTING FEATURES", "=")
    print("✓ 500+ programming languages supported (via Pygments)")
    print("✓ Automatic language detection from code blocks and tool results")
    print("✓ Theme-aware semantic color mapping")
    print("✓ Consistent highlighting across all themes")
    print("✓ Graceful fallback if Pygments not installed")
    print("✓ Modular architecture: detection → tokenization → mapping → styling")
    print("\nLanguages shown in this demo:")
    for lang in SAMPLE_CODE.keys():
        print(f"  • {lang}")
    print("\nFor complete list, see: https://pygments.org/languages/")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

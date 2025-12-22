# Security Guidelines for OAuth Development

## ⚠️ CRITICAL: Credential Protection

This repository implements OAuth authentication for the Anthropic SDK, which involves handling sensitive credentials. **NEVER commit real credentials to git.**

### Protected Credential Types

1. **API Keys**: `sk-ant-api*` - Pay-per-token authentication
2. **OAuth Access Tokens**: `sk-ant-oat01-*` - Subscription authentication
3. **OAuth Refresh Tokens**: `sk-ant-ort01-*` - Token renewal
4. **Credentials Files**: `~/.claude/.credentials.json`

## Multi-Layer Protection System

### Layer 1: .gitignore
- Blocks credentials files at filesystem level
- Prevents accidental `git add`
- See `.gitignore` for full list

### Layer 2: Pre-commit Hooks
- Scans commits before they're created
- Detects patterns: `sk-ant-*`, credential file names
- Blocks commits containing secrets

**Setup**:
```bash
pip install pre-commit
pre-commit install
```

### Layer 3: Gitleaks Scanner
- Deep scan for secrets using regex patterns
- Runs locally and in CI/CD

**Setup**:
```bash
# Install gitleaks
brew install gitleaks  # macOS
# OR download from: https://github.com/gitleaks/gitleaks/releases

# Scan repository
gitleaks detect --source . --verbose
```

### Layer 4: GitHub Secret Scanning
- Automatic scanning by GitHub (if enabled)
- Alerts on push if secrets detected
- Enable in: Settings → Security → Code security and analysis

## Development Workflow

### ✅ Safe Practices

1. **Use environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with real values (NEVER commit .env)
   ```

2. **Use mock credentials in tests**:
   ```python
   MOCK_ACCESS_TOKEN = "sk-ant-oat01-xxxxx-MOCK-TOKEN-FOR-TESTING"
   ```

3. **Store real credentials outside repo**:
   - Use `~/.claude/.credentials.json` (already gitignored globally)
   - Reference via environment variables

4. **Never hardcode credentials**:
   ```python
   # ❌ NEVER DO THIS
   api_key = "sk-ant-api01-abc123..."

   # ✅ DO THIS
   api_key = os.environ.get("ANTHROPIC_API_KEY")
   ```

### ❌ Dangerous Practices

- ❌ Committing `.env` files with real values
- ❌ Hardcoding tokens in source code
- ❌ Copying `~/.claude/.credentials.json` into repo
- ❌ Storing credentials in comments or documentation
- ❌ Pasting real tokens in commit messages

## Branch Strategy

- **main**: Public branch, synced with upstream
- **dev/oauth-private**: Development branch (keep local, don't push)
- When ready to share: Create sanitized branch with all credentials removed

## Emergency: Credential Leaked

If you accidentally commit a credential:

1. **Immediately revoke the credential**:
   - API Key: https://console.anthropic.com/settings/keys
   - OAuth: Log out from Claude Code CLI (`claude logout`)

2. **Remove from git history**:
   ```bash
   # For recent commit
   git reset --soft HEAD~1
   git reset HEAD path/to/file

   # For older commits (use BFG or git-filter-repo)
   # DO NOT PUSH until credentials are removed!
   ```

3. **Notify maintainers** if already pushed to GitHub

## Testing Credentials

Use these safe patterns in tests:

```python
# tests/fixtures/mock_credentials.json
{
  "claudeAiOauth": {
    "accessToken": "sk-ant-oat01-MOCK_TOKEN_DO_NOT_USE_IN_PRODUCTION",
    "refreshToken": "sk-ant-ort01-MOCK_REFRESH_DO_NOT_USE_IN_PRODUCTION",
    "expiresAt": 9999999999999,
    "scopes": ["user:inference", "user:profile"],
    "subscriptionType": "max"
  }
}
```

## CI/CD Security

When setting up GitHub Actions:

1. Use **GitHub Secrets** for sensitive values
2. Never echo secrets in logs
3. Use `gitleaks` in CI pipeline
4. Require secret scanning pass before merge

## Questions?

If unsure whether something is safe to commit, **don't commit it**. Ask first!

## Resources

- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Pre-commit](https://pre-commit.com/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [git-secrets](https://github.com/awslabs/git-secrets)

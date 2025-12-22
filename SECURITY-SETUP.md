# Security Setup Guide

## ✅ Protection Status

Your repository now has **5 layers of credential protection**:

### Layer 1: Enhanced .gitignore ✓
**Status**: Active
**Protection**: Blocks credential files at filesystem level

**Blocked patterns**:
- `sk-ant-*` (all Anthropic tokens)
- `*credentials*.json`
- `.env` files
- `*.key`, `*.pem` files
- API key/token file patterns

**Test**:
```bash
# This should be ignored
echo "sk-ant-api01-test" > test_key.txt
git status  # Should NOT show test_key.txt
```

---

### Layer 2: Pre-commit Hooks ✓
**Status**: Needs installation
**Protection**: Scans every commit before creation

**Setup** (required):
```bash
# Install pre-commit
pip install pre-commit

# Install the hooks
pre-commit install

# Test it works
pre-commit run --all-files
```

**Features**:
- Gitleaks secret scanning
- Detect-secrets baseline
- Custom Anthropic token pattern detection
- Large file prevention
- Private key detection

**Test**:
```bash
# Try to commit a fake key (should be blocked)
echo "sk-ant-api01-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" > test.py
git add test.py
git commit -m "test"  # Should FAIL
```

---

### Layer 3: Gitleaks Scanner ✓
**Status**: Needs installation
**Protection**: Deep secret scanning

**Setup** (recommended):
```bash
# macOS
brew install gitleaks

# Windows (via Scoop)
scoop install gitleaks

# OR download binary from:
# https://github.com/gitleaks/gitleaks/releases
```

**Usage**:
```bash
# Scan entire repo
gitleaks detect --source . --verbose

# Scan before push
gitleaks protect --staged --verbose
```

---

### Layer 4: GitHub Actions CI/CD ✓
**Status**: Active (when pushed to GitHub)
**Protection**: Automated scanning on every push/PR

**Workflow**: `.github/workflows/security-scan.yml`

**What it does**:
1. Runs Gitleaks on full git history
2. Runs detect-secrets scan
3. Checks for Anthropic credential patterns
4. Blocks PR if secrets detected

**Enable**:
- Automatically runs when you push to GitHub
- No additional setup required

---

### Layer 5: GitHub Secret Scanning
**Status**: Needs manual activation
**Protection**: GitHub native secret detection

**Setup** (do this now):
1. Go to your GitHub repo: https://github.com/RoscoeTheDog/claude-agent-sdk-python
2. Click **Settings** → **Security** → **Code security and analysis**
3. Enable **Secret scanning**
4. Enable **Push protection** (prevents pushes with secrets)
5. Enable **Dependency graph**
6. Enable **Dependabot alerts**

---

## Branch Strategy

### Current Setup
- ✅ **main** branch: Public, synced with upstream
- ✅ **dev/oauth-private** branch: Local development (DON'T PUSH)

### Safe Workflow

```bash
# Work on private branch (current)
git checkout dev/oauth-private

# Develop with real credentials locally
# All changes stay local - DON'T PUSH THIS BRANCH

# When ready to share (after sanitizing):
git checkout main
git checkout -b feature/oauth-public
# Cherry-pick safe commits only
git cherry-pick <commit-hash>  # Only commits without credentials
git push origin feature/oauth-public
```

---

## Installation Checklist

Run these commands now:

```bash
# 1. Install pre-commit
pip install pre-commit
pre-commit install

# 2. Install gitleaks (choose your platform)
# macOS:
brew install gitleaks

# Windows (Scoop):
scoop install gitleaks

# Windows (Manual): Download from https://github.com/gitleaks/gitleaks/releases

# 3. Test the protection
pre-commit run --all-files

# 4. Scan for existing secrets
gitleaks detect --source . --verbose
```

---

## Testing Your Protection

### Test 1: .gitignore
```bash
echo "sk-ant-api01-test123" > .credentials.json
git status
# Should show: nothing to commit (file ignored)
rm .credentials.json
```

### Test 2: Pre-commit Hook
```bash
echo 'API_KEY = "sk-ant-api01-xxx"' > test_file.py
git add test_file.py
git commit -m "test"
# Should FAIL with: "ERROR: Found Anthropic API key pattern!"
git reset HEAD test_file.py
rm test_file.py
```

### Test 3: Gitleaks
```bash
gitleaks detect --source . --verbose
# Should pass with: "No leaks found"
```

---

## Emergency Procedures

### If You Accidentally Commit a Credential

**STOP! Don't push!**

1. **Revoke the credential immediately**:
   - API Key: https://console.anthropic.com/settings/keys
   - OAuth: `claude logout` in terminal

2. **Remove from git history**:
   ```bash
   # If it's the last commit
   git reset --soft HEAD~1
   git reset HEAD path/to/file.py

   # If it's in older commits
   # Use BFG Repo-Cleaner or git-filter-repo
   ```

3. **Verify it's gone**:
   ```bash
   gitleaks detect --source . --verbose
   ```

4. **Generate new credential** and continue

---

## Daily Development Checklist

Before each coding session:
- [ ] Confirm on `dev/oauth-private` branch
- [ ] Pre-commit hooks installed (`pre-commit --version`)
- [ ] Real credentials only in `~/.claude/.credentials.json` (never in repo)

Before each commit:
- [ ] Review `git diff` for accidental credentials
- [ ] Pre-commit hooks will auto-scan
- [ ] If blocked, remove secrets and retry

---

## Resources

- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [Pre-commit Documentation](https://pre-commit.com/)
- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [SECURITY.md](./SECURITY.md) - Full security guidelines

---

## Questions?

If you're unsure whether something is safe to commit, **DON'T COMMIT IT**. The protection layers will catch most issues, but human review is the best defense.

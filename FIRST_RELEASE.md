# First Release Setup Guide

This is a **one-time setup** guide for the srsdb project maintainer to enable automated PyPI releases.

## ⚠️ You Must Do This Before Running `python release.py`

The automated release system requires PyPI Trusted Publishing to be configured first.

## Setup Instructions (5 minutes)

### 1. Create PyPI Account (if needed)

If you don't have a PyPI account:
- Go to https://pypi.org/account/register/
- Create an account
- Verify your email

### 2. Configure Trusted Publishing

1. **Log in to PyPI**: https://pypi.org/

2. **Go to Publishing Settings**:
   - Visit: https://pypi.org/manage/account/publishing/
   - Or navigate: Account Settings → Publishing

3. **Add New Pending Publisher** with these **exact** settings:

   ```
   PyPI Project Name:  srsdb
   Owner:             jomof
   Repository name:    srsdb
   Workflow name:      release.yml
   Environment name:   pypi
   ```

4. **Click "Add"**

   The publisher will show as "pending" - this is normal!
   It will activate automatically on the first successful release.

### 3. Verify Setup

Check that you see:
```
✅ Pending publisher for srsdb
   Repository: jomof/srsdb
   Workflow: release.yml
   Environment: pypi
```

### 4. You're Done!

Now you can run releases with:

```bash
python release.py
```

The script will automatically:
- Bump the version
- Create a git commit and tag
- Push to GitHub
- Trigger the release workflow
- Publish to PyPI

## What Happens on First Release

1. **First time**: The pending publisher becomes active
2. **Package is published**: https://pypi.org/project/srsdb/
3. **Future releases**: Just run `python release.py` - no additional setup needed!

## Troubleshooting

### "Publisher not found" error

If you get this error, double-check:
- PyPI project name is exactly: `srsdb` (lowercase)
- Owner is exactly: `jomof`
- Repository name is exactly: `srsdb`
- Workflow name is exactly: `release.yml`
- Environment name is exactly: `pypi`

### Still having issues?

See the full troubleshooting guide in [RELEASING.md](RELEASING.md#troubleshooting)

## After Configuring Trusted Publishing

Once you've added the pending publisher on PyPI, you need to trigger a release.

**IMPORTANT**: The version in `pyproject.toml` has been updated to 0.6.0 to match the other files. The previous mismatch (pyproject.toml had 0.1.0 while setup.py had 0.6.0) caused PyPI to publish version 0.1.0 instead of 0.6.0.

### Option 1: Re-trigger v0.6.0 (recommended)

Since pyproject.toml is now fixed, you can re-trigger the v0.6.0 release:

```bash
# Commit the pyproject.toml fix and re-create the tag
git add pyproject.toml release.py .github/workflows/release.yml
git commit -m "Fix: Update pyproject.toml version and improve version verification"
git tag -d v0.6.0
git push origin :refs/tags/v0.6.0
git tag -a v0.6.0 -m "Release version 0.6.0"
git push origin main
git push origin v0.6.0
```

### Option 2: Create a new release

If you prefer to create a fresh release:

```bash
# First commit the fixes
git add pyproject.toml release.py .github/workflows/release.yml
git commit -m "Fix: Update pyproject.toml version and improve version verification"
git push origin main

# Then create a new release
python release.py patch  # Creates v0.6.1
```

## After First Release

Once the first release succeeds:
- The pending publisher becomes active
- Package appears on PyPI: https://pypi.org/project/srsdb/
- Future releases only require: `python release.py`
- GitHub release is created automatically
- Installation verification runs automatically

That's it! The hard part is done. Future releases are one command.

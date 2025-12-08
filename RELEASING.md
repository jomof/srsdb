# Release Process

This document describes how to create a new release of srsdb.

## Prerequisites

1. **PyPI Account**: You need a PyPI account with maintainer access to the srsdb package
2. **PyPI Trusted Publishing**: Must be configured (see setup instructions below)
3. **GitHub Permissions**: You need push access to the repository and ability to create tags
4. **Clean Working Directory**: All changes must be committed before creating a release

## ⚠️ FIRST-TIME SETUP: PyPI Trusted Publishing

**IMPORTANT**: Before your first release, you must configure PyPI Trusted Publishing. This is a one-time setup.

### Step-by-Step Setup

1. **Go to PyPI**: Visit https://pypi.org/manage/account/publishing/

2. **Add a new pending publisher** with these exact settings:
   - **PyPI Project Name**: `srsdb`
   - **Owner**: `jomof`
   - **Repository name**: `srsdb`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`

3. **Save** - The publisher will be in "pending" state until the first successful publish

4. **Done!** - Now you can run releases

### Why This is Required

This setup allows GitHub Actions to publish to PyPI without storing API tokens. It's more secure and is the recommended approach for modern Python packages.

## Release Workflow

The release process uses:
- `release.py` - Python script that bumps the version, creates a git tag, and pushes to GitHub
- `.github/workflows/release.yml` - GitHub Actions workflow that publishes to PyPI when a tag is pushed

**The entire process is automatic** - just run `python release.py` and it handles everything!

### Step 1: Prepare the Release

Ensure all changes are committed and tests pass:

```bash
# Run all tests
python -m unittest discover -v

# Ensure working directory is clean
git status
```

### Step 2: Run Release Script

Use the `release.py` script to bump the version and trigger the release:

```bash
# Bump minor version (0.1.0 -> 0.2.0) - default
python release.py

# Bump major version (0.1.0 -> 1.0.0)
python release.py major

# Bump patch version (0.1.0 -> 0.1.1)
python release.py patch
```

The script will automatically:
1. ✅ Read the current version from `__init__.py`
2. ✅ Calculate the new version
3. ✅ Ask for confirmation
4. ✅ Update version in `__init__.py` and `setup.py`
5. ✅ Commit the version bump
6. ✅ Create a git tag (e.g., `v0.2.0`)
7. ✅ **Push commit to GitHub**
8. ✅ **Push tag to GitHub (triggers release workflow)**

That's it! The script handles everything automatically.

### Step 3: GitHub Actions Workflow

When you push a tag, the `.github/workflows/release.yml` workflow automatically:

1. **Builds the package**
   - Creates source distribution (`.tar.gz`)
   - Creates wheel distribution (`.whl`)
   - Validates the distributions

2. **Publishes to PyPI**
   - Uses trusted publishing (OIDC)
   - Uploads to https://pypi.org/project/srsdb/

3. **Creates GitHub Release**
   - Attaches distribution files
   - Generates release notes
   - Marks as stable release

4. **Verifies Installation**
   - Tests installation on Python 3.8-3.12
   - Verifies imports work
   - Tests optional Ebisu dependency

### Step 4: Verify the Release

After the workflow completes (usually 2-5 minutes):

1. **Check PyPI**: Visit https://pypi.org/project/srsdb/
2. **Check GitHub Release**: Visit https://github.com/jomof/srsdb/releases
3. **Test Installation**:

```bash
# In a fresh virtual environment
python -m venv test_env
source test_env/bin/activate
pip install srsdb
python -c "import srsdb; print(srsdb.__version__)"

# Test with Ebisu
pip install srsdb[ebisu]
python -c "from srsdb import EbisuDatabase; print('Success!')"
```

## Notes on Trusted Publishing

The release workflow uses PyPI's Trusted Publishing (OIDC), which you configured in the first-time setup above. This is more secure than using API tokens because:

- No secrets are stored in GitHub
- GitHub cryptographically proves the workflow's identity to PyPI
- Permissions are scoped to specific workflows
- Automatically rotates credentials

If you need to modify the trusted publisher settings later, visit https://pypi.org/manage/project/srsdb/settings/publishing/

## Troubleshooting

### Version Mismatch Error

If the workflow fails with a version mismatch:

```bash
# Check current versions
grep __version__ __init__.py
grep version setup.py
git tag -l
```

Ensure all three match the expected version.

### Failed PyPI Upload

If PyPI upload fails:

1. Check workflow logs in GitHub Actions
2. Verify trusted publishing is configured
3. Ensure the version doesn't already exist on PyPI
4. Check that the package builds cleanly: `python -m build`

### Tag Already Exists

If you need to recreate a tag:

```bash
# Delete local tag
git tag -d v0.2.0

# Delete remote tag
git push origin :refs/tags/v0.2.0

# Recreate tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

**Note**: Only do this if the tag hasn't been published to PyPI yet!

## Manual Release (Emergency)

If the automated workflow fails, you can release manually:

```bash
# Build the package
python -m build

# Check the distribution
twine check dist/*

# Upload to PyPI (requires API token)
twine upload dist/*
```

## Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **Major** (X.0.0): Breaking changes, incompatible API changes
- **Minor** (0.X.0): New features, backward compatible
- **Patch** (0.0.X): Bug fixes, backward compatible

Examples:
- `0.1.0 -> 0.2.0`: Added new algorithm implementation
- `0.2.0 -> 0.2.1`: Fixed bug in existing algorithm
- `0.9.0 -> 1.0.0`: First stable release

## Release Checklist

Before each release:

- [ ] All tests pass (`python -m unittest discover -v`)
- [ ] Documentation is updated
- [ ] CHANGELOG is updated (if exists)
- [ ] Version number is appropriate for changes
- [ ] Working directory is clean
- [ ] You're on the main branch

After release:

- [ ] PyPI package is live
- [ ] GitHub release is created
- [ ] Installation verification passed
- [ ] Announcement sent (if applicable)

#!/usr/bin/env python3
"""
Release script for srsdb - bumps version and creates a git tag.

Usage:
    python release.py        # Bump minor version (0.1.0 -> 0.2.0)
    python release.py major  # Bump major version (0.1.0 -> 1.0.0)
    python release.py patch  # Bump patch version (0.1.0 -> 0.1.1)
"""

import re
import sys
import subprocess
from pathlib import Path


def get_current_version():
    """Read the current version from srsdb/__init__.py"""
    init_file = Path(__file__).parent / "srsdb" / "__init__.py"
    content = init_file.read_text()

    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        raise ValueError("Could not find __version__ in srsdb/__init__.py")

    return match.group(1)


def parse_version(version):
    """Parse version string into (major, minor, patch) tuple"""
    parts = version.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        raise ValueError(f"Invalid version format: {version}")


def bump_version(version, bump_type='minor'):
    """Bump the version according to bump_type"""
    major, minor, patch = parse_version(version)

    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Use 'major', 'minor', or 'patch'")


def update_version_in_file(file_path, old_version, new_version):
    """Update version in a file"""
    content = file_path.read_text()

    # Update __version__ in __init__.py
    if file_path.name == '__init__.py':
        pattern = r'(__version__\s*=\s*["\'])' + re.escape(old_version) + r'(["\'])'
        replacement = r'\g<1>' + new_version + r'\g<2>'
        new_content = re.sub(pattern, replacement, content)

    # Update version in setup.py
    elif file_path.name == 'setup.py':
        pattern = r'(version\s*=\s*["\'])' + re.escape(old_version) + r'(["\'])'
        replacement = r'\g<1>' + new_version + r'\g<2>'
        new_content = re.sub(pattern, replacement, content)

    # Update version in pyproject.toml
    elif file_path.name == 'pyproject.toml':
        pattern = r'(version\s*=\s*["\'])' + re.escape(old_version) + r'(["\'])'
        replacement = r'\g<1>' + new_version + r'\g<2>'
        new_content = re.sub(pattern, replacement, content)
    else:
        return False

    if content != new_content:
        file_path.write_text(new_content)
        return True
    return False


def run_command(cmd, check=True):
    """Run a shell command and return the result"""
    print(f"Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        check=False
    )

    if result.returncode != 0 and check:
        print(f"Error: {result.stderr}")
        sys.exit(1)

    return result


def check_git_status():
    """Check if git working directory is clean"""
    result = run_command("git status --porcelain", check=False)
    if result.stdout.strip():
        print("Error: Working directory is not clean. Commit or stash changes first.")
        print(result.stdout)
        sys.exit(1)


def create_tag(version):
    """Create a git tag for the version"""
    tag_name = f"v{version}"

    # Check if tag already exists
    result = run_command(f"git tag -l {tag_name}", check=False)
    if result.stdout.strip():
        print(f"Error: Tag {tag_name} already exists")
        sys.exit(1)

    # Create tag
    run_command(f'git tag -a {tag_name} -m "Release version {version}"')
    print(f"✅ Created tag: {tag_name}")

    return tag_name


def main():
    # Parse arguments
    bump_type = 'minor'  # Default
    if len(sys.argv) > 1:
        bump_type = sys.argv[1].lower()
        if bump_type not in ('major', 'minor', 'patch'):
            print(f"Usage: {sys.argv[0]} [major|minor|patch]")
            print(f"  Default: minor")
            sys.exit(1)

    # Get current version
    current_version = get_current_version()
    print(f"Current version: {current_version}")

    # Calculate new version
    new_version = bump_version(current_version, bump_type)
    print(f"New version: {new_version} ({bump_type} bump)")

    # Confirm
    response = input(f"\nProceed with release {new_version}? [y/N] ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    # Check git status
    print("\n📋 Checking git status...")
    check_git_status()

    # Update version in files
    print("\n📝 Updating version in files...")
    root = Path(__file__).parent

    updated_files = []
    for file_path in [root / "srsdb" / "__init__.py", root / "setup.py", root / "pyproject.toml"]:
        if file_path.exists():
            if update_version_in_file(file_path, current_version, new_version):
                print(f"  ✅ Updated {file_path.relative_to(root)}")
                updated_files.append(str(file_path.relative_to(root)))
            else:
                print(f"  ⚠️  No changes in {file_path.relative_to(root)}")

    if not updated_files:
        print("Error: No files were updated")
        sys.exit(1)

    # Commit changes
    print("\n📦 Committing version bump...")
    run_command(f"git add {' '.join(updated_files)}")
    run_command(f'git commit -m "Bump version to {new_version}"')
    print(f"  ✅ Committed version bump")

    # Create tag
    print("\n🏷️  Creating git tag...")
    tag_name = create_tag(new_version)

    # Push changes
    print("\n🚀 Pushing to GitHub...")

    # Get current branch
    result = run_command("git branch --show-current", check=False)
    current_branch = result.stdout.strip() or "main"

    # Push commit
    print(f"  Pushing commit to {current_branch}...")
    result = run_command(f"git push origin {current_branch}", check=False)
    if result.returncode != 0:
        print(f"  ⚠️  Warning: Failed to push commit")
        print(f"  {result.stderr}")
        print("\n  You may need to push manually:")
        print(f"    git push origin {current_branch}")
        print(f"    git push origin {tag_name}")
        sys.exit(1)
    print(f"  ✅ Pushed commit to {current_branch}")

    # Push tag (this triggers the release workflow)
    print(f"  Pushing tag {tag_name}...")
    result = run_command(f"git push origin {tag_name}", check=False)
    if result.returncode != 0:
        print(f"  ⚠️  Warning: Failed to push tag")
        print(f"  {result.stderr}")
        print("\n  You may need to push the tag manually:")
        print(f"    git push origin {tag_name}")
        sys.exit(1)
    print(f"  ✅ Pushed tag {tag_name}")

    # Success
    print("\n" + "=" * 60)
    print("✨ Release triggered successfully!")
    print("=" * 60)
    print(f"\nVersion released: {current_version} → {new_version}")
    print(f"Tag pushed: {tag_name}")
    print("\n🎯 GitHub Actions workflow triggered!")
    print("\nThe release workflow will now:")
    print("  1. Build the package")
    print("  2. Publish to PyPI")
    print("  3. Create GitHub release")
    print("  4. Verify installation")
    print("\nMonitor progress at:")
    print(f"  https://github.com/jomof/srsdb/actions")
    print(f"\nOnce complete, the package will be available at:")
    print(f"  https://pypi.org/project/srsdb/{new_version}/")
    print()


if __name__ == "__main__":
    main()

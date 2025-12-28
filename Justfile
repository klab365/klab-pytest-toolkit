NETWORK_MODE := "--net host"
CMD_ENV := if path_exists('/.dockerenv') == "false" { 'docker run --init --rm --user $(id -u):$(id -g) --group-add $(stat -c "%g" /var/run/docker.sock) -v $(pwd):/workspaces/klab-pytest-toolkit -v /var/run/docker.sock:/var/run/docker.sock -e UV_CACHE_DIR=${UV_CACHE_DIR:-/tmp/.cache/uv} ' + NETWORK_MODE + ' -w /workspaces/klab-pytest-toolkit klab-pytest-toolkit-build' } else { '' }

# Build ci docker
build-ci-docker user-id='1000':
    docker build \
        -t klab-pytest-toolkit-build \
        --target ci \
        --file Dockerfile \
        --build-arg UID={{user-id}} \
        .

# Clean project
clean:
    rm -rf .pytest_cache
    rm -rf .mypy_cache
    rm -rf __pycache__
    rm -rf packages/**/__pycache__
    rm -rf packages/*/__pycache__
    rm -rf htmlcov
    rm -rf coverage.xml
    rm -rf pytest.xml

# Runs linting for python code
lint:
    {{ CMD_ENV }} uv run ty check .
    {{ CMD_ENV }} uv run ruff check .

# Formats you code with Black, and sorts imports with isort
format:
    {{ CMD_ENV }} uv run ruff format .
    {{ CMD_ENV }} uv run ruff check --fix .

# Checks if the code is formatted correctly
check-format:
    {{ CMD_ENV }} uv run ruff check .
    {{ CMD_ENV }} uv run ruff format --check .

# run pytest with coverage
test args='':
    {{ CMD_ENV }} xvfb-run --auto-servernum uv run pytest \
        --junitxml=pytest.xml \
        --cov-report=term-missing:skip-covered \
        --cov-report=xml:coverage.xml \
        --cov=packages \
        {{ args }} \
        packages

# Update version in all packages
update-version version:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Updating all packages to version {{version}}"
    for pkg in packages/*/; do
        echo "Processing package $pkg"
        pkg_name=$(basename $pkg)
        init_file=$(find $pkg/src -name __init__.py | head -n1)
        if [ -f "$init_file" ]; then
            echo "Updating $pkg_name"
            sed -i 's/__version__ = .*/__version__ = "{{version}}"/' "$init_file"
        fi
    done

# Build all packages
build:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Cleaning previous builds..."
    rm -rf dist
    mkdir -p dist

    echo "Building all packages..."
    for pkg in packages/*/; do
        if [ -f "${pkg}pyproject.toml" ]; then
            echo "Building $(basename $pkg)..."
            {{ CMD_ENV }} uv build "$pkg"
        fi
    done
    
    echo "Collecting distributions..."
    for pkg in packages/*/; do
        if [ -d "${pkg}dist" ]; then
            cp "${pkg}dist"/* dist/ 2>/dev/null || true
        fi
    done
    
    echo "Build complete!"
    ls -lh dist/

# Publish to PyPI (requires PYPI_TOKEN environment variable)
publish token *args='':
    @echo "Publishing to PyPI..."
    {{ CMD_ENV }} uv publish dist/* --token {{token}} {{args}}

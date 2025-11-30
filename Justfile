NETWORK_MODE := "--net host"
CMD_ENV := if path_exists('/.dockerenv') == "false" { 'docker run --rm --user $(id -u):$(id -g) --group-add $(stat -c "%g" /var/run/docker.sock) -v $(pwd):/workspaces/klab-pytest-toolkit -v /var/run/docker.sock:/var/run/docker.sock ' + NETWORK_MODE + ' -w /workspaces/klab-pytest-toolkit klab-pytest-toolkit-build' } else { '' }

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
    git clean -fdX .

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
test:
    {{ CMD_ENV }} uv run pytest \
        --junitxml=pytest.xml \
        --cov-report=term-missing:skip-covered \
        --cov-report=xml:coverage.xml \
        --cov=packages \
        packages

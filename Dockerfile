FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS ci

ARG UID=1000

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN <<EOF
    apt-get update
    apt-get install -y --no-install-recommends sudo

    # add user dev with specified UID
    useradd -m -u ${UID} dev

    # add dev user to sudoers
    echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

    # Install tkinter for python
    apt install -y python3-tk

    # Install headless UI Tests dependencies
    apt-get install -y --no-install-recommends xvfb xdotool x11-utils xauth

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF

# Copy docker CLI
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker


FROM ci AS development

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN <<EOF
    apt-get update
    apt-get install -y --no-install-recommends git zsh locales ssh curl

    # install just
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

    # Ensure locale is set to UTF-8
    apt update
    apt install -y locales
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
    locale-gen en_US.UTF-8
    update-locale LANG=en_US.UTF-8

    # Setup shell for dev user
    chsh -s /bin/zsh dev
    su - dev -c 'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended'
    su - dev -c 'git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions'
    su - dev -c 'sed -i "s/plugins=(git)/plugins=(git zsh-autosuggestions)/" ~/.zshrc'
    curl -sS https://starship.rs/install.sh | sh -s -- --yes
    su - dev -c 'echo "eval \"\$(starship init zsh)\"" >> ~/.zshrc'

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF


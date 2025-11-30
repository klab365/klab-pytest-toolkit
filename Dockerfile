FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS ci

ARG UID=1000

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN <<EOF
    apt-get update
    apt-get install -y --no-install-recommends \
        curl

    # install just
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to /usr/local/bin

    # add user dev with specified UID
    useradd -m -u ${UID} dev

    apt-get clean
    rm -rf /var/lib/apt/lists/*
EOF


FROM ci AS development

SHELL ["/bin/bash", "-euo", "pipefail", "-c"]

RUN <<EOF
    apt-get update
    apt-get install -y --no-install-recommends \
        git sudo zsh locales ssh

    # Ensure locale is set to UTF-8
    apt update
    apt install -y locales
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen
    locale-gen en_US.UTF-8
    update-locale LANG=en_US.UTF-8

    # add dev user to sudoers
    echo "dev ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

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


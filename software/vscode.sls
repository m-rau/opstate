vscode_prerequisites:
  pkg.installed:
    - refresh: True
    - pkgs:
        - software-properties-common
        - apt-transport-https
        - wget

vscode_install:
  cmd.run:
    - name: |
        cd /tmp
        wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
        install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
        sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
        apt update -y
        apt install code -y
    - creates: /usr/bin/code

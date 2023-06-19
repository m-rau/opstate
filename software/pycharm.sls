pycharm_prerequisites:
  pkg.installed:
    - refresh: True
    - pkgs:
        - wget

pycharm_install:
  archive.extracted:
    - name: /opt/pycharm/
    - source: https://download.jetbrains.com/python/pycharm-community-2023.1.2-aarch64.tar.gz
    - source_hash: md5=e061ea52d6269e3ced2e96e699806433
    - user: root
    - group: users
    - enforce_toplevel: false
    - if_missing: /opt/pycharm/pycharm-community-2023.1.2

/opt/pycharm/latest:
  file.symlink:
    - target: /opt/pycharm/pycharm-community-2023.1.2

/usr/sbin/pycharm:
  file.symlink:
    - target: /opt/pycharm/latest/bin/pycharm.sh
    
/usr/share/applications/jetbrains-pycharm-ce.desktop:
  file.managed:
    - mode: 755
    - contents: |
        [Desktop Entry]
        Version=1.0
        Type=Application
        Name=PyCharm Community Edition
        Icon=/opt/pycharm/latest/bin/pycharm.svg
        Exec="/opt/pycharm/latest/bin/pycharm.sh" %f
        Comment=Python IDE for Professional Developers
        Categories=Development;IDE;
        Terminal=false
        StartupWMClass=jetbrains-pycharm-ce
        StartupNotify=true

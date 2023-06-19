# see https://techviewleo.com/install-mongodb-on-ubuntu-linux/

mongodb_prerequisites:
  pkg.installed:
    - refresh: True
    - pkgs:
        - wget
        - curl 
        - gnupg2
        - software-properties-common
        - apt-transport-https
        - ca-certificates
        - lsb-release
        - runit

mongodb_install:
  cmd.run:
    - name: |
        cd /tmp
        test -f /etc/apt/trusted.gpg.d/mongodb-6.gpg && rm /etc/apt/trusted.gpg.d/mongodb-6.gpg
        wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc |  gpg --dearmor | sudo tee /usr/share/keyrings/mongodb.gpg > /dev/null
        echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
        apt update
        apt install mongodb-org -y
    - creates: /usr/bin/mongod

/srv/mongodb:
  file.directory:
    - mode: 750
    - makedirs: True
    - user: mongodb
    - group: root

/srv/mongodb/log:
  file.directory:
    - mode: 750
    - makedirs: True
    - user: mongodb
    - group: root

/etc/logrotate.d/mongodb.conf:
  file.managed:
    - contents: |
        /srv/mongodb/log/* {
            daily
            size 50M
            compress
            copytruncate
            rotate 7
        }

/srv/mongodb/data:
  file.directory:
    - mode: 750
    - makedirs: True
    - user: mongodb
    - group: root

mongodb_keyfile:
  cmd.run:
    - name: |
        cd /srv/mongodb
        openssl rand -base64 768 > keyfile
        chown mongodb:root keyfile
        chmod 400 keyfile
    - creates: /srv/mongodb/keyfile

/etc/security/limits.d/mongo.conf:
  file.managed:
    - contents: |
        mongodb            hard    nofile          64000
        mongodb            soft    nofile          64000
    - user: root
    - group: root

/srv/mongodb/local.conf:
  file.managed:
    - contents: |
        systemLog:
            destination: file
            logAppend: true
            logRotate: reopen
            path: "/srv/mongodb/log/mongodb.log"
        storage:
            dbPath: "/srv/mongodb/data"
            engine: "wiredTiger"
        net:
            port: 27017
            bindIp: 0.0.0.0
        processManagement:
            pidFilePath: "/srv/mongodb/mongod.lock"
            timeZoneInfo: /usr/share/zoneinfo
        replication:
           oplogSizeMB: 1000
           replSetName: rs0
    - mode: 755
    - user: mongodb
    - group: root

mongodb_setup:
  cmd.script:
    - source: salt://software/mongodb/setup_mongo.sh
    - creates: /srv/mongodb/.protected

/etc/sv/mongodb:
  file.directory:
    - mode: 750
    - makedirs: True

/etc/sv/mongodb/run:
  file.managed:
    - mode: 750
    - contents: |
        #!/bin/sh

        ulimit -n 64000
        exec chpst -umongodb /usr/bin/mongod --config /srv/mongodb/local.conf --auth --keyFile /srv/mongodb/keyfile

/etc/service/mongodb:
  file.symlink:
    - target: /etc/sv/mongodb

mongodb_service:
  cmd.run:
    - name: |
        until sv start mongodb;
        do
          sleep 1
        done
    - onlyif: |
        sv s mongodb | grep -v "run: mongodb"

mongodb_restart:
  cmd.run:
    - name: |
        sv restart mongodb
    - onchanges:
      - file: /etc/sv/mongodb/run
      - file: /srv/mongodb/local.conf



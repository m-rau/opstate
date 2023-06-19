#!/bin/bash

BIN=/usr/bin/mongod
MONGO_SHELL=/usr/bin/mongosh

function alive {
    until echo "quit();" | $MONGO_SHELL --host 127.0.0.1 --port 27017;
    do
      sleep 1
    done
}

function kill_mongo {
    while ps -C mongod > /dev/null; do killall $BIN; done
}

# if already protected -> do nothing
if [ -f /srv/mongodb/.protected ]; then
    echo "already protected"
    exit 0 
fi

# if [ -d /etc/sv/mongodb ]; then
#     sv down mongodb
# fi

echo "kill existing mongodb service (step 1)"
kill_mongo

echo "start service (step 1)"
/usr/bin/chpst -u mongodb $BIN --fork -f /srv/mongodb/local.conf
alive

cat > protect.js <<- .
use admin
rs.initiate()
rs.status()
db.createUser(
    {
        user: "eroc",
        pwd: "eroc",
        roles: [ { role: "root", db: "admin" } ]
    }
);
.

echo "enable protection"
$MONGO_SHELL --host 127.0.0.1 --port 27017 admin < protect.js
rm protect.js

kill_mongo
touch /srv/mongodb/.protected

# if [ -d /etc/sv/mongodb ]; then
#     sv up mongodb
# fi

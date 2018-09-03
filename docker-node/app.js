"use strict";

// Dependency
const fs = require('fs');
const https = require('https');

// Path for publicly available files
let CONFIG_PUBLIC_PATH = 'public';
process.argv.forEach(function (val, index, array) {
    if(index == 2) {
        CONFIG_PUBLIC_PATH = val
        console.log('Starting web server for path : ' + CONFIG_PUBLIC_PATH)
    }
});

// Https server
const HTTPS_PORT = 8888;
let serverConfig = {
    key: fs.readFileSync('key.pem'),
    cert: fs.readFileSync('cert.pem'),
};
let serverRequestHandle = function(request, response) {
    let filepath = CONFIG_PUBLIC_PATH.concat(request.url);
    if(filepath == (CONFIG_PUBLIC_PATH + '/')) {
        filepath = CONFIG_PUBLIC_PATH + '/index.html';
    }
    fs.access(filepath, (err) => {
        if (err) {
            if (err.code === 'ENOENT') {
                response.writeHead(404, { 'Content-Type': 'text/plain' });
                response.end('404 not found\n');
                return;
            }
            throw err;
        }

        if (filepath.endsWith('css')) {
            response.writeHead(200, {'Content-Type': 'text/css'});
        } else {
            response.writeHead(200, {'Content-Type': 'text/html'});
        }
        response.end(fs.readFileSync(filepath));
    });
};


let httpsServer = https.createServer(serverConfig, serverRequestHandle);
httpsServer.listen(HTTPS_PORT, '0.0.0.0');


//MDTMP const WebSocketServer = require('ws').Server;
//MDTMP
/*
// WebSocket server
let wss = new WebSocketServer({server: httpsServer});
wss.on('connection', function(ws) {
    ws.on('message', function(message) {
    wss.broadcast(message);
    });
});
wss.broadcast = function(data) {
    for(let i in this.clients) {
        this.clients[i].send(data);
    }
};
*/


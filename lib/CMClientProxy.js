var Steam = require("steam-client");
var fs = require('fs');
var winston = require('winston');

class CMClient extends Steam.CMClient {

    constructor(options, protocol){
        super(protocol);
        this.options = options;
    }

    connect(server, autoRetry) {
        if (typeof server === 'boolean') {
            autoRetry = server;
            server = null;
        }
        server = server || null;
        if (server === null) {
            try {
                var file = this.options.dataDirectory + "/servers.json";
                var srvs = JSON.parse(fs.readFileSync(file));
                server = srvs[Math.floor(Math.random() * srvs.length)]  
            } catch (error) {
                server = null;
                console.log(error);
            }
            
        }
        winston.debug(`connecting to ${server.host}:${server.port}`);
        super.connect(server, autoRetry);
    }
}

module.exports = CMClient;
const http = require('http');
const qs = require('qs')
const awsIot = require('aws-iot-device-sdk');


const hostname = '127.0.0.1';
const port = 8080;

var device = awsIot.device({
   keyPath: 'nfc-gateway.private.key',
  certPath: 'nfc-gateway.cert.pem',
    caPath: 'root.pem',
  clientId: 'nfc-gateway',
   host: 'a1454obf7awdo8.iot.us-east-1.amazonaws.com'
});

const server = http.createServer((req, res) => {
   if (req.method === 'POST') {
	   
	   var body = '';
	   
		req.on('data', function (data) {
            body += data;
            console.log("Partial body: " + body);
        });
		req.on('end', function () {
            console.log("Body: " + body);
			var queryData = qs.parse(body);
			console.log(queryData);
			device.publish('nfcdata', JSON.stringify({ data: queryData.d, modem: queryData.m}));
		
        });
        
		res.statusCode = 200;
		res.setHeader('Content-Type', 'text/plain');
		res.end('OK\n');
			
		
    }
});

device.on('connect', function() {
    
	console.log('connect');
	
	server.listen(port, hostname, () => {
		console.log(`Server running at http://${hostname}:${port}/`);
	});

});
  





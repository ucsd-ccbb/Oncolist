var express = require('express'),
    app = express(),
    path = require('path'),
    request = require('request');

app.use(express.static(__dirname + '/Prototype2'));

app.get('/', function(req, res) {
    res.sendFile('prototype2C.html', {
        'root': __dirname + '/Prototype2'
    });
});

app.listen(3000)

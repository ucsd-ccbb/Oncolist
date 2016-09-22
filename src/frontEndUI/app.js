var express = require('express');
var app = express();
var path = require('path');
var request = require('request');
var mongo = require('mongodb');
var monk = require('monk');

//var db = monk('52.32.253.172:27017/cache');
//var db = monk('52.24.205.32:27017/cache');
var db = monk('127.0.0.1:27017/cache');

var fs = require('fs');

var masterList = [];
var geoList = [];

//for (var i = 0; i<69779; i++) {
//    var esId = 2020000000 + i;
//    masterList.push(esId);
//    if(i % 200 == 0){
//        console.log(esId);
//    }
//}

//TCGA LOUVAIN
//for (var i = 0; i<15142; i++) {
//    var esId = 2020000000 + i;
//    //geoList.push(esId);
//    masterList.push(esId);
//    if(i % 200 == 0){
//        console.log(esId);
//    }
//}

//TCGA OSLOM
for (var i = 0; i<23229; i++) {
    var esId = 2040000000 + i;
    //geoList.push(esId);
    masterList.push(esId);
    if(i % 200 == 0){
        console.log(esId);
    }
}

//GEO OSLOM
for (var i = 0; i<30939; i++) {
    var esId = 2020000000 + i;
    //geoList.push(esId);
    masterList.push(esId);
    if(i % 200 == 0){
        console.log(esId);
    }
}

//GEO LOUVAIN
//for (var i = 0; i<14403; i++) {
//    var esId = 2010000000 + i;
    //geoList.push(esId);
//    masterList.push(esId);
//    if(i % 200 == 0){
//        console.log(esId);
//    }
//}

//TCGA LOUVAIN
//for (var i = 0; i<14691; i++) {
//    var esId = 2030000000 + i;
    //geoList.push(esId);
//    masterList.push(esId);
//    if(i % 200 == 0){
//        console.log(esId);
//    }
//}

//masterList.push(2020035401);
//masterList.push(2020061695);
//masterList.push(2020034060);
//masterList.push(2020033661);
//masterList.push(2020035052);

app.use(function(req,res,next){
    req.db = db;
    next();
});

app.use(express.static(__dirname + '/Prod',{ maxAge: 1000 }));

var bodyParser = require('body-parser');

app.use(bodyParser.json({limit: '50mb'}));
app.use(bodyParser.urlencoded({
  limit: '50mb',
    extended: true
}));

/*
app.get('/', function(req, res) {
    res.sendFile('prototype2C.html', {
        'root': __dirname + '/Prod'
    });
});
*/

app.get('/thumbnails/:imageFile', function(req, resp) {
    //var filePath = path.join(__dirname, 'Prod', 'thumbnails', req.params.imageFile);
    var filePath = path.join(__dirname, '.', 'thumbnails', req.params.imageFile);
    try {
        fs.accessSync(filePath, fs.F_OK);
        //console.log("found file");
        resp.sendFile(req.params.imageFile, {
            'root': path.join(__dirname, 'thumbnails')
        });
    } catch (e) {
        //console.log("didn't find file");
        //console.log(e);
        resp.sendFile('blank.png', {
            'root': __dirname
        });
    }
});

app.get('/setThumbnailList/:hitIds', function(req, resp) {
  var hitIds = req.params.hitIds;

  var addThese = hitIds.split(",");

  for(var i=0;i<addThese.length;i++){
    masterList.push(addThese[i]);
  }

  console.log(masterList.length);
  resp.send({"status": "success"});
});

app.get('/getRenderedNodes/:hitId', function(req, res) {
  var hitId = req.params.hitId;

  var db = req.db;
  var collection = db.get('nodesWithLocation');

  collection.find({"nodesId": hitId},{},function(e,docs){
    if(docs.length > 0){
      //console.log(req.query.callback);
      //response.write(params.callback + '(' + JSON.stringify(rows) + ')');
      if(req.query.callback === null){
        res.send(JSON.stringify({"data": docs[0]["data"]}));
      } else {
        res.send(req.query.callback + '(' + JSON.stringify({"data": docs[0]["data"]}) + ')');
      }
    } else {
      res.send({"data": []});
    }
  });
});

app.post('/saveNodeLocation/:nodeLocationsId', function(req, resp) {
    var nodeLocationsId = req.params.nodeLocationsId;

    var myNodes = req.body.nodeArray;
    var myEdges = req.body.edgesArray;

    var data = //req.body.data;
    {
      edges: myEdges,
      nodes: myNodes
      //edges: JSON.parse(myEdges),
      //nodes: JSON.parse(myNodes)
    };

    console.log(data);

    var db = req.db;
    var collection = db.get('nodesWithLocation');

    collection.insert({
        "nodesId" : nodeLocationsId,
        "data" : data
      }, function (err, doc) {
        if (err) {
            // If it failed, return error
            resp.send("There was a problem adding the information to the database.");
        }
        else {
            // And forward to success page
            resp.status(200);

            console.log(masterList.length);

            resp.redirect('../partials/processor_VisJS_heatmap.html?geneList=PLACEHOLDER&clusterId=' + masterList.pop());
        }
    });
});

app.post('/saveImg/:imageId/:nodeLocationsId', function(req, resp) {
    var imageId = req.params.imageId;
    var nodeLocationsId = req.params.nodeLocationsId;
    /*

    var myNodes = req.body.nodeArray;
    var myEdges = req.body.edgesArray;

    //console.log("edges: " + myEdges);
    //console.log("nodes: " + myNodes);


    var data = //req.body.data;
    {
      edges: myEdges,
      nodes: myNodes
      //edges: JSON.parse(myEdges),
      //nodes: JSON.parse(myNodes)
    };

    //console.log(data);

    var db = req.db;
    var collection = db.get('nodesWithLocation');

    collection.insert({
        "nodesId" : nodeLocationsId,
        "data" : data
      }, function (err, doc) {
        if (err) {
            // If it failed, return error
            resp.send("There was a problem adding the information to the database.");
        }
        else {
*/

            if(imageId === "ABCDEF") {
              resp.redirect('../../partials/processor_VisJS_heatmap.html?clusterId=' + masterList.pop());
            } else {
                var img64 = req.body.img64;

                var db = req.db;
                var collection = db.get('thumbnails');

                var imageBuffer = decodeBase64Image(img64);

                fs.writeFile("thumbnails/" + imageId + ".png", imageBuffer.data, function(err) {
                    if(err != null){
                        console.log(err);
                    }
                });
                if(masterList.length > 0){
                    resp.status(200);
                    console.log(masterList.length);
                    resp.redirect('../../partials/processor_VisJS_heatmap.html?clusterId=' + masterList.pop());
                } else {
                    resp.end();
                }
            }

    /*
        }
    });

    */
});

app.get('/getImg/:imageId', function(req, res) {
    var imageId = req.params.imageId;
    console.log("Here is my image ID: " + imageId);
    var db = req.db;
    var collection = db.get('thumbnails');

    collection.find({"thumbId": imageId},{},function(e,docs){
        var imageBuffer = decodeBase64Image(docs[0]["base64Data"]);

        fs.writeFile(imageId + ".png", imageBuffer.data, function(err) {
          if(err != null){
            console.log(err);
          }
        });

        res.send({"bufferData": docs[0]["base64Data"]});
    });
});

app.get('/getMessage/:myMessage', function(req, res) {
 var myMessage = req.params.myMessage;
 res.send(myMessage);
});

function decodeBase64Image(dataString) {
  var matches = dataString.match(/^data:([A-Za-z-+\/]+);base64,(.+)$/);
  var response = {};
  if (matches.length !== 3) {
    return new Error('Invalid input string');
  }

  response.type = matches[1];
  response.data = new Buffer(matches[2], 'base64');
  return response;
}

var router = express.Router();

router.param('user_id', function(req, res, next, id) {
  // sample user, would actually fetch from DB, etc...
  req.user = {
    id: id,
    name: 'TJ'
  };
  next();
});

app.get('/xsaveImg', function(req, res) {
  var db = req.db;
  var collection = db.get('thumbnails');

  collection.insert({
        "thumbId" : "temp1",
        "base64Data" : "iVBORw0KGgoAAAANSUhEUgAAB+kAAATcCAYAAABI9LdtAAAgAElEQVR4Xuzde5SWZb0//jcDMyCoCKKgBp4yD6mpYbXtoO3C8yE1Qc30m1qZu1a7tpadzbSV7cqt2/x+00q21t5keWCLWWpuLdNfwe6AluAJM0kQlPPBmWHmt+5nHAfwBATXPMO87rVmCTz3c3+u63V/lv+857quPu3t7e1xESBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAhtcoI+QfoMbK0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBGoCQnqNQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAgJBeDxAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAgUICQvpC0MoQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAEhvR4gQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQKFBIT0haCVIUCAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECQno9QIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECgkI6QtBK0OAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBIT0eoAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBQSENIXglaGAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgI6fUAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAoJCCkLwStDAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQENLrAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgUEhASF8IWhkCBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQICCk1wMECBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKCQgJC+ELQyBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEBASK8HCBAgQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQIBAIQEhfSFoZQgQIECAAAECBAgQIECAAAECBAgQIECAAA…gQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAkL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCQgpE8ErQwBAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIEBDSmwECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIJBIQEifCFoZAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECAgpDcDBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIEAgkYCQPhG0MgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAQEhvBggQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAQCIBIX0iaGUIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgICQ3gwQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAIFEAgYj69oAAAE3SURBVEL6RNDKECBAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABIb0ZIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECiQSE9ImglSFAgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAkJ6M0CAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBBIJCOkTQStDgAABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgSE9GaAAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgkEhDSJ4JWhgABAgQIECBAgAABAgQIECBAgAABAgQIECBAgAABAgQICOnNAAECBAgQIECAAAECBAgQIECAAAECBAgQIECAAAECBAgQSCTw/wGkKroztFBLmwAAAABJRU5ErkJggg=="
    }, function (err, doc) {
        if (err) {
            // If it failed, return error
            res.send("There was a problem adding the information to the database.");
        }
        else {
            // And forward to success page
            res.send("Success");
        }
    });
});

app.get('/saveGeoImg', function(req, res) {
    img64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAD8GlDQ1BJQ0MgUHJvZmlsZQAAOI2NVd1v21QUP4lvXKQWP6Cxjg4Vi69VU1u5GxqtxgZJk6XpQhq5zdgqpMl1bhpT1za2021Vn/YCbwz4A4CyBx6QeEIaDMT2su0BtElTQRXVJKQ9dNpAaJP2gqpwrq9Tu13GuJGvfznndz7v0TVAx1ea45hJGWDe8l01n5GPn5iWO1YhCc9BJ/RAp6Z7TrpcLgIuxoVH1sNfIcHeNwfa6/9zdVappwMknkJsVz19HvFpgJSpO64PIN5G+fAp30Hc8TziHS4miFhheJbjLMMzHB8POFPqKGKWi6TXtSriJcT9MzH5bAzzHIK1I08t6hq6zHpRdu2aYdJYuk9Q/881bzZa8Xrx6fLmJo/iu4/VXnfH1BB/rmu5ScQvI77m+BkmfxXxvcZcJY14L0DymZp7pML5yTcW61PvIN6JuGr4halQvmjNlCa4bXJ5zj6qhpxrujeKPYMXEd+q00KR5yNAlWZzrF+Ie+uNsdC/MO4tTOZafhbroyXuR3Df08bLiHsQf+ja6gTPWVimZl7l/oUrjl8OcxDWLbNU5D6JRL2gxkDu16fGuC054OMhclsyXTOOFEL+kmMGs4i5kfNuQ62EnBuam8tzP+Q+tSqhz9SuqpZlvR1EfBiOJTSgYMMM7jpYsAEyqJCHDL4dcFFTAwNMlFDUUpQYiadhDmXteeWAw3HEmA2s15k1RmnP4RHuhBybdBOF7MfnICmSQ2SYjIBM3iRvkcMki9IRcnDTthyLz2Ld2fTzPjTQK+Mdg8y5nkZfFO+se9LQr3/09xZr+5GcaSufeAfAww60mAPx+q8u/bAr8rFCLrx7s+vqEkw8qb+p26n11Aruq6m1iJH6PbWGv1VIY25mkNE8PkaQhxfLIF7DZXx80HD/A3l2jLclYs061xNpWCfoB6WHJTjbH0mV35Q/lRXlC+W8cndbl9t2SfhU+Fb4UfhO+F74GWThknBZ+Em4InwjXIyd1ePnY/Psg3pb1TJNu15TMKWMtFt6ScpKL0ivSMXIn9QtDUlj0h7U7N48t3i8eC0GnMC91dX2sTivgloDTgUVeEGHLTizbf5Da9JLhkhh29QOs1luMcScmBXTIIt7xRFxSBxnuJWfuAd1I7jntkyd/pgKaIwVr3MgmDo2q8x6IdB5QH162mcX7ajtnHGN2bov71OU1+U0fqqoXLD0wX5ZM005UHmySz3qLtDqILDvIL+iH6jB9y2x83ok898GOPQX3lk3Itl0A+BrD6D7tUjWh3fis58BXDigN9yF8M5PJH4B8Gr79/F/XRm8m241mw/wvur4BGDj42bzn+Vmc+NL9L8GcMn8F1kAcXgSteGGAAAAlklEQVRoBe2S0QnAIBDFrPvvbEtHCATkiP8vcInP+d4a8PaAG/4TOuS2khWpiGSgryWJxdiKYHXSsCKSWIytCFYnDSsiicXYimB10rAikliMrQhWJw0rIonF2IpgddKwIpJYjK0IVicNKyKJxdiKYHXSsCKSWIytCFYnDSsiicXYimB10rAikliMrQhWJw0rIonF2DFFXjzEBGCQom4fAAAAAElFTkSuQmCC";
    var imageId = 123;
    var imageBuffer = decodeBase64Image(img64);

    console.log(geoList.length);
    for(var i=0; i < geoList.length; i++){
        imageId = geoList[i];
        console.log(imageId);
        for(var j=0;j<10000000;j++){}

        fs.writeFileSync("thumbnails/" + imageId + ".png", imageBuffer.data);//, function(err) {
    }

    res.send("Success");
});

router.route('/drive')
.all(function(req, res, next) {
  console.log("running the ALL method");
  // runs for all HTTP verbs first
  // think of it as route specific middleware!
  next();
})
.get(function(req, res, next) {
  console.log("running the GET method");
  res.json({message: 'GET Done'});
})
.post(function(req, res, next) {
  res.json({message: 'POST Done'});
});

router.route('/oauth2callback')
.all(function(req, res, next) {
  console.log("running the ALL method");
  // runs for all HTTP verbs first
  // think of it as route specific middleware!
  next();
})
.get(function(req, res, next) {
  console.log("running the GET method");
  res.json({message: 'GET oauth2callback Done'});
})
.post(function(req, res, next) {
  res.json({message: 'POST oauth2callback Done'});
});

router.route('/users/:user_id')
.all(function(req, res, next) {
  console.log("running the ALL method");
  // runs for all HTTP verbs first
  // think of it as route specific middleware!
  next();
})
.get(function(req, res, next) {
  console.log("running the GET method");
  //req.user.name = req.params.user_id;
  // save user ... etc
  res.json(req.user);
  //res.send('<p>hey</p>');
  //res.json(req.user);
})
.put(function(req, res, next) {
  // just an example of maybe updating the user
  req.user.name = req.params.name;
  // save user ... etc
  res.json(req.user);
})
.post(function(req, res, next) {
  next(new Error('not implemented'));
})
.delete(function(req, res, next) {
  next(new Error('not implemented'));
});

app.use(router);

app.listen(3000)


var app = angular.module('myApp', ['services']);


// Code borrowed from stackoverflow user Anthony O. - May 15th 2014
app.config(['$httpProvider', function($httpProvider) {
    if (!$httpProvider.defaults.headers.get) {
        $httpProvider.defaults.headers.get = {};
    }
    $httpProvider.defaults.headers.get['If-Modified-Since'] = 'Mon, 26 Jul 1997 05:00:00 GMT';
    $httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
    $httpProvider.defaults.headers.get['Pragma'] = 'no-cache';
}]);

app.filter('cut', function () {
      return function (value, wordwise, max, tail) {
          if (!value) return '';

          max = parseInt(max, 10);
          if (!max) return value;
          if (value.length <= max) return value;

          value = value.substr(0, max);
          if (wordwise) {
              var lastspace = value.lastIndexOf(' ');
              if (lastspace != -1) {
                  value = value.substr(0, lastspace);
              }
          }

          return value + (tail || ' …');
      };
  });


/*
==========================================================================================================
==========================================================================================================
==========================================================================================================
==========================================================================================================
==========================================================================================================
========================================= MAIN CONTROLLER ================================================
==========================================================================================================
==========================================================================================================
==========================================================================================================
==========================================================================================================
==========================================================================================================
*/

app.controller('myCtrl', function ($scope, $http, $log, $filter, HttpServiceJsonp, $location, $timeout, $window) {
  //$scope.pythonHost = "http://localhost:8182"; // Localhost
  $scope.pythonHost = python_host_global;
  //$scope.pythonHost = "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com"; // PROD
  //$scope.pythonHost = "http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com"; //Search Engine (Dev)
  $scope.info = {"TermId": "",
    "termDescription": "",
    "currentTab": "unknown",
    "activateDrugbank": false,
    "activateGenecard": false,
    "phenotype_info": [],
    "snps": "",
    "people_publications": [],
    "showMorePublications": false,
    "selectedNode": "",
    "highlightActive": false,
    "selectedAuthorTitle": "Select Author",
    "selectedGeneTitle": "Select Gene",
    "selectedClusterTitle": "Select Cluster",
    "selectedClusterColor": "blank",
    "clusterId": ""
  };
  $scope.showMore = {
    "origin": "modalWindow"
  };
  $scope.d3root;
  $scope.geneList;
  $scope.svg;
  $scope.zoom;
  $scope.force;
  $scope.fisheye;
  $scope.d3link;
  $scope.d3link2;
  $scope.node;
  $scope.result;
  $scope.nodes;
  $scope.edges;
  $scope.node2;
  $scope.nodeg;
  $scope.circle;
  $scope.w;
  $scope.h;
  $scope.nominal_stroke;
  $scope.allNodes;
  $scope.allEdges;
  $scope.network;
  $scope.item;
  $scope.dropdownAuthorNodes = [];
  $scope.dropdownGeneNodes = [];
  $scope.ClusterByColor = [];
  $scope.lastClusterZoomLevel = 0;
  $scope.clusterFactor = 0.9;
  $scope.clusterIndex = 0;
  $scope.cluster = {
    "clusters": []
  };


    function GetQueryStringParams(sParam)
    {
        var sPageURL = window.location.search.substring(1);
        var sURLVariables = sPageURL.split('&');
        for (var i = 0; i < sURLVariables.length; i++)
        {
            var sParameterName = sURLVariables[i].split('=');
            if (sParameterName[0] == sParam)
            {
                return sParameterName[1];
            }
        }
    }

    //$scope.init_page = function(){ //http://localhost:63343/Prototype2/prototype2C.html#?savedId=563a8343f6f4071f79300231
    //};

    $scope.updateGene = function(itemId, itemLabel){
      var params = {nodes: null};


      $scope.info.selectedClusterTitle = "Select Cluster";
      $scope.info.selectedClusterColor = "blank";
      $scope.info.selectedGeneTitle = itemLabel;
      $scope.info.selectedAuthorTitle = "Select Author";

      if(itemId != "-1"){
        params.nodes = [itemId];

        neighbourhoodHighlight(params);
      }
    };

    $scope.updateAuthor = function(itemId, itemLabel){
      var params = {nodes: null};


      $scope.info.selectedClusterTitle = "Select Cluster";
      $scope.info.selectedClusterColor = "blank";
      $scope.info.selectedGeneTitle = "Select Gene";
      $scope.info.selectedAuthorTitle = itemLabel;

      if(itemId != "-1"){
        params.nodes = [itemId];

        neighbourhoodHighlight(params);
      }
    };

    $scope.update2 = function(){
      var params = {nodes: null};

      if($scope.item[0] != "-1"){
        params.nodes = [$scope.item];

        neighbourhoodHighlight(params);
      }
    };

    $scope.selectCluster = function(colorId) {
      //alert(colorId);
      var i=0;
      clusterIdArray = [];

      $scope.info.selectedClusterTitle = "Cluster";
      $scope.info.selectedClusterColor = colorId;
      $scope.info.selectedGeneTitle = "Select Gene";
      $scope.info.selectedAuthorTitle = "Select Author";

      for (var nodeId in $scope.allNodes) {
        if($scope.allNodes[nodeId].permaColor === colorId && $scope.geneList.indexOf($scope.allNodes[nodeId].permaLabel) > -1 ){
          clusterIdArray.push($scope.allNodes[nodeId].id);
        }
      }

      $scope.ClusterHighlight(clusterIdArray);
    };

    $scope.openInNewWindow = function() {
      $window.open("http://geneli.st/partials/VisJS_heatmap.html?geneList=OR2J3&termId=my%20title&clusterId=" + $scope.info.clusterId + "&networkTitle=my%20title&origin=newWindow");

    }

    $scope.openExport = function() {
      var url = $scope.pythonHost + "/ds/getheatmapgraph/" + $scope.info.clusterId;
      $window.open(url);
    }

    $scope.init_page = function(){ //http://localhost:63343/Prototype2/prototype2C.html#?savedId=563a8343f6f4071f79300231
      var termId = GetQueryStringParams('termId');
      $scope.geneList = GetQueryStringParams('geneList');
      var bp_network_title = GetQueryStringParams('networkTitle');
      bp_network_title = bp_network_title.replace("%20", " ");
      $scope.info.clusterId = GetQueryStringParams("clusterId");

      $scope.showMore.origin = GetQueryStringParams("origin");

      // create a DataSet
      $("#selectAuthor").val("-1");

      var options = {};

      var data = new vis.DataSet(options);
      $('#heatmapIsLoading').html('<span class="fa fa-spinner fa-2x fa-pulse"></span>');
      //var url = $scope.pythonHost + "/ds/getbpnet/" + $scope.geneList + "?callback=JSON_CALLBACK";
      var url = $scope.pythonHost.replace("8182","3000") + "/getRenderedNodes/" + $scope.info.clusterId + "?callback=JSON_CALLBACK";
      var myrequest = HttpServiceJsonp.jsonp(url)
           .success(function (result) {
             $scope.result = result;
             console.log(result["data"]);

             $scope.w = (window.innerWidth > 0) ? window.innerWidth : screen.width;
             $scope.h = (window.innerHeight > 0) ? window.innerHeight + 30 : screen.height + 30;  //600,

             $scope.w = $scope.w - 20;
             $scope.h = $scope.h - 60;

             $('#heatmap').width($scope.w);
             $('#heatmap').height($scope.h);
             //$('#heatmap').width(800);
             //$('#heatmap').height(800);

             $scope.nodeArray = JSON.parse(result["data"]["nodes"]);
             $scope.edgeArray = JSON.parse(result["data"]["edges"]);

             for(var i=0;i<$scope.nodeArray.length;i++){
                 $scope.nodeArray[i]

             }

              var nodesDataset = new vis.DataSet($scope.nodeArray);
              var edgesDataset = new vis.DataSet($scope.edgeArray);

              //var container = document.getElementById('mynetwork');
              var container = document.getElementById('heatmap');
              var options = {
                nodes: {
                  shape: 'dot',
                  scaling: {
                    min: 10,
                    max: 30,
                    label: {
                      min: 8,
                      max: 30,
                      drawThreshold: 12,
                      maxVisible: 20
                    }
                  },
                  font: {
                    size: 28,
                    face: 'Tahoma'
                  }
                },
                edges: {
                  width: 0.15,
                  color: {inherit: 'from'},
                  smooth: {
                    type: 'continuous'
                  }
                },
                physics: false,
                interaction: {
                  tooltipDelay: 200,
                  hideEdgesOnDrag: true
                }
              };
              var data = {nodes:nodesDataset, edges:edgesDataset}

              $scope.network = new vis.Network(container, data, options);

              $scope.network.fit();

              $timeout(function() {
                $('#heatmapIsLoading').html('');
              }, 100);


           }).finally(function () {
      }).error(function (data, status, headers, config) {
          alert(data + ' - ' + status + ' - ' + headers);
      });

    };

    $scope.getNodeLocation = function(){
      var nodePositions = $scope.network.getPositions();

      for (var property in $scope.allNodes) {
          if ($scope.allNodes.hasOwnProperty(property)) {
            $scope.allNodes[property].x = nodePositions[property].x;
            $scope.allNodes[property].y = nodePositions[property].y;

            $scope.nodeArray[property].x  = nodePositions[property].x;
            $scope.nodeArray[property].y  = nodePositions[property].y;

            //console.log($scope.nodeArray);
            //console.log($scope.allNodes[property]);
          }
      }
      console.log($scope.nodeArray);

      var my_form = document.createElement('FORM');
      my_form.name='myForm';
      my_form.method='POST';
      my_form.action='http://localhost:3000/saveNodeLocation/' + $scope.info.clusterId;
      my_tb=document.createElement('INPUT');
      my_tb.type='TEXT';
      my_tb.name='nodeLocations';
      my_tb.value=JSON.stringify($scope.nodeArray);
      my_form.appendChild(my_tb);

      document.body.appendChild(my_form);
      my_form.submit();

      my_form.parentNode.removeChild(my_form);


/*
      for(var i=0;i<$scope.allNodes.length;i++){
        $scope.allNodes[i].x = nodePositions[i].x;
        $scope.allNodes[i].y = nodePositions[i].y;
      }

      console.log($scope.allNodes);
*/

      //console.log(nodePositions);
    }

    $scope.saveNetworkImage = function() {

        //$('#heatmap').width(2000);
        //$('#heatmap').height(2000);
        //console.log($scope.network.getScale());
        $scope.network.setSize(1200,1200);
        $scope.network.redraw();
        $scope.network.fit();

        var moveToOpts = {
                    "position": {"x":750, "y":750},
                    "scale": 1.0,
                    "offset": {"x":0, "y":0},
                    "animation": false
                  };


        $scope.network.moveTo(moveToOpts);

        //$scope.network.fit();

        //console.log($scope.network.getScale());
        var canvas = document.querySelector("canvas");
        var context = canvas.getContext('2d');

        var w = canvas.width;
        var h = canvas.height;

        var data;

        //get the current ImageData for the canvas.
        data = context.getImageData(0, 0, w, h);

        //store the current globalCompositeOperation
        var compositeOperation = context.globalCompositeOperation;

        //set to draw behind current content
        context.globalCompositeOperation = "destination-over";

        //set background color
        context.fillStyle = "#ffffff";

        //draw background / rect on entire canvas
        context.fillRect(0,0,w,h);

        //var image = canvas.toDataURL("image/png").replace("image/png", "image/octet-stream");  // here is the most important part because if you dont replace you will get a DOM 18 exception.

        var image = new Image();
        image.src = canvas.toDataURL("image/png");

        var anchor = document.createElement('a');

        console.log(anchor);
        anchor.setAttribute('href', image.src);
        anchor.setAttribute('target', "_blank");

        context.globalCompositeOperation = compositeOperation;

        var doc = new jsPDF();

      	doc.addImage(image.src, 'JPEG', 10, 10, 200, 200, undefined, "fast");
        doc.save("Images.pdf");

        //anchor.setAttribute('download', 'image.png');
        //anchor.click();
        //$("#saveImageDiv").src = canvas.toDataURL("image/png");
        //$('#heatmap').width($scope.w);
        //$('#heatmap').height($scope.h);
        $scope.network.setSize($scope.w,$scope.h);

        moveToOpts = {
                "position": {"x":0, "y":0},
                "scale": 1.0,
                "offset": {"x":0, "y":0},
                "animation": false
              };


        $scope.network.moveTo(moveToOpts);


        //$scope.network.fit();

        //window.location.href=image; // it will save locally
    };





    $scope.exportData2 = function(){
      $('#table-div').html("<table id='basic-table'><tr><td>1</td><td>Donna</td><td>Moore</td><td>dmoore0@furl.net</td><td>China</td><td>211.56.242.221</td></tr><tr><td>1</td><td>Donna</td><td>Moore</td><td>dmoore0@furl.net</td><td>China</td><td>211.56.242.221</td></tr></table>");

      //$timeout(function() {
        var doc = new jsPDF('p', 'pt');
        var elem = document.getElementById("basic-table");
        var res = doc.autoTableHtmlToJson(elem);
        doc.autoTable(res.columns, res.data);
        doc.save("table.pdf");
      //}, 500);
      };


    $scope.exportData = function(){
      var exportArrayString = "data:text/csv;charset=utf-8,";
      var tempHeader = "NODES\nnode_name,community_id,degree";
      exportArrayString += tempHeader + '\n';

      var tableNodeTempString = "<table id='node-table'>";

      tableNodeTempString += "<thead><tr><th>node_name</th><th>community_id</th><th>degree</th></tr></thead>";

      //var doc = new jsPDF();
      //doc.setFontSize(16);
      //doc.text(20, 20, 'NODES:');
      //doc.setFontSize(12);
      //doc.text(20, 30, 'node_name');
      //doc.text(65, 30, 'community_id');
      //doc.text(110, 30, 'degree');

      //node_page_location = 40 + ($scope.result.nodes.length * 7) + 20;
      for (var i = 0; i < $scope.result.nodes.length; i++) {
        tableNodeTempString += "<tr><td>" + $scope.result.nodes[i]["id"] + "</td><td>" + $scope.result.nodes[i]["com"] + "</td><td>" + $scope.result.nodes[i]["degree"] + "</td></tr>";
        //doc.text(20, 40 + (i * 7), $scope.result.nodes[i]["id"])
        //doc.text(65, 40 + (i * 7), $scope.result.nodes[i]["com"].toString())
        //doc.text(110, 40 + (i * 7), $scope.result.nodes[i]["degree"].toString());
          exportArrayString += "" + $scope.result.nodes[i]["id"] + "," + $scope.result.nodes[i]["com"] + "," + $scope.result.nodes[i]["degree"] + '\n';
      }

      tableNodeTempString += "</table>";



      exportArrayString += '\n\n\n\n\n';

      var tempHeader = "EDGES\nsource,target,weight";

      exportArrayString += tempHeader + '\n';

      //doc.setFontSize(16);
      //doc.text(20, node_page_location, 'EDGES:');
      //doc.setFontSize(12);
      //node_page_location += 10;
      //doc.text(20, node_page_location, 'source');
      //doc.text(65, node_page_location, 'target');
      //doc.text(110, node_page_location, "weight"  + "\n");

      //node_page_location += 10;

      var tableEdgeTempString = "<table id='edge-table'>";

      tableEdgeTempString += "<thead><tr><th>source</th><th>target</th><th>weight</th></tr></thead>";

      for (var j = 0; j < $scope.result.links.length; j++) {
        tableEdgeTempString += "<tr><td>" + $scope.result.links[j]["source"] + "</td><td>" + $scope.result.links[j]["target"] + "</td><td>" + $scope.result.links[j]["weight"] + "</td></tr>";
        //doc.text(20, node_page_location + (j * 7), $scope.result.links[j]["source"].toString());
        //doc.text(65, node_page_location + (j * 7), $scope.result.links[j]["target"].toString());
        //doc.text(110, node_page_location + (j * 7), $scope.result.links[j]["weight"].toString() + "\n");

        //node_page_location
          exportArrayString += "" + $scope.result.links[j]["source"] + "," + $scope.result.links[j]["target"] + "," + $scope.result.links[j]["weight"] + '\n';
      }

      var encodedUri = encodeURI(exportArrayString);

      var doc = new jsPDF('p', 'pt');

      doc.setFontSize(14);
      doc.text(40, 30, 'NODES:');
      doc.setFontSize(12);
      $('#table-div').html(tableNodeTempString);
      var elem = document.getElementById("node-table");
      var res = doc.autoTableHtmlToJson(elem);
      doc.autoTable(res.columns, res.data);

      doc.addPage();

      doc.setFontSize(14);
      doc.text(40, 30, 'EDGES:');
      doc.setFontSize(12);
      $('#table-div').html(tableEdgeTempString);
      var elemEdge = document.getElementById("edge-table");
      var resEdge = doc.autoTableHtmlToJson(elemEdge);
      doc.autoTable(resEdge.columns, resEdge.data);

      doc.save("table.pdf");

      //doc.save('Test.pdf');

      //window.open(encodedUri);
    };

    function selectEdge(params){
      var selectedNode = params.edges[0];
      // the main node gets its own color and its label back.
      //console.log(params);
      for (var nodeId in $scope.allEdges) {
        if ($scope.allEdges[nodeId].id === selectedNode) {
          $scope.allEdges[nodeId].label = $scope.allEdges[nodeId].title;

          var updateArray = [];
          for (nodeId in $scope.allEdges) {
            if ($scope.allEdges.hasOwnProperty(nodeId)) {
              updateArray.push($scope.allEdges[nodeId]);
            }
          }
          $scope.edges.update(updateArray);
          //document.getElementById('eventSpan').innerHTML = '<h2>Correlation value: </h2>' + $scope.allEdges[nodeId].title + ' D3:' + d3.event.pageX;
        } else {
          $scope.allEdges[nodeId].label = '';
        }
      }
    }

    function showMyPopup(id){

    }

    function hideMyPopup(){

    }

    function neighbourhoodHighlight(params) {
      // if something is selected:
      //alert($scope.network.getSeed());
      if (params.nodes.length > 0) {
        $scope.info.highlightActive = true;
        var i,j;
        var selectedNode = params.nodes[0];


        if ($scope.$root.$$phase != '$apply' && $scope.$root.$$phase != '$digest') {
          $scope.$apply(function(){
            $scope.info.selectedNode = $scope.allNodes[selectedNode].label;
          });
        }

        var degrees = 2;

        // mark all nodes as hard to read.
        for (var nodeId in $scope.allNodes) {
          $scope.allNodes[nodeId].color = 'rgba(200,200,200,0.5)';
          if ($scope.allNodes[nodeId].hiddenLabel === undefined) {
            $scope.allNodes[nodeId].hiddenLabel = $scope.allNodes[nodeId].label;
            $scope.allNodes[nodeId].label = undefined;
          }
        }
        var connectedNodes = $scope.network.getConnectedNodes(selectedNode);
        var allConnectedNodes = [];

        // get the second degree nodes
        for (i = 1; i < degrees; i++) {
          for (j = 0; j < connectedNodes.length; j++) {
            allConnectedNodes = allConnectedNodes.concat($scope.network.getConnectedNodes(connectedNodes[j]));
          }
        }

        // all second degree nodes get a different color and their label back
        for (i = 0; i < allConnectedNodes.length; i++) {
          $scope.allNodes[allConnectedNodes[i]].color = 'rgba(150,150,150,0.75)';
          if ($scope.allNodes[allConnectedNodes[i]].hiddenLabel !== undefined) {
            $scope.allNodes[allConnectedNodes[i]].label = $scope.allNodes[allConnectedNodes[i]].hiddenLabel;
            $scope.allNodes[allConnectedNodes[i]].hiddenLabel = undefined;
          }
        }

        // all first degree nodes get their own color and their label back
        for (i = 0; i < connectedNodes.length; i++) {
          $scope.allNodes[connectedNodes[i]].color = undefined;
          if ($scope.allNodes[connectedNodes[i]].hiddenLabel !== undefined) {
            $scope.allNodes[connectedNodes[i]].label = $scope.allNodes[connectedNodes[i]].hiddenLabel;
            $scope.allNodes[connectedNodes[i]].color = $scope.allNodes[connectedNodes[i]].permaColor;
            $scope.allNodes[connectedNodes[i]].hiddenLabel = undefined;
          }
        }

        // the main node gets its own color and its label back.
        $scope.allNodes[selectedNode].color = $scope.allNodes[selectedNode].permaColor;
        if ($scope.allNodes[selectedNode].hiddenLabel !== undefined) {
          $scope.allNodes[selectedNode].label = $scope.allNodes[selectedNode].hiddenLabel;
          $scope.allNodes[selectedNode].color = $scope.allNodes[selectedNode].permaColor;
          $scope.allNodes[selectedNode].hiddenLabel = undefined;
        }
      }
      else if ($scope.info.highlightActive === true) {
        // reset all nodes
        $scope.$apply(function(){
          $scope.info.selectedNode = "";

          $scope.info.selectedClusterTitle = "Select Cluster";
          $scope.info.selectedClusterColor = "blank";
          $scope.info.selectedGeneTitle = "Select Gene";
          $scope.info.selectedAuthorTitle = "Select Author";
        });

        for (var nodeId in $scope.allNodes) {
          $scope.allNodes[nodeId].color = $scope.allNodes[nodeId].permaColor;
          if ($scope.allNodes[nodeId].hiddenLabel !== undefined) {
            $scope.allNodes[nodeId].label = $scope.allNodes[nodeId].hiddenLabel;
            $scope.allNodes[nodeId].hiddenLabel = undefined;
          }
        }
        $scope.info.highlightActive = false
      }

      // transform the object into an array
      var updateArray = [];
      for (nodeId in $scope.allNodes) {
        if ($scope.allNodes.hasOwnProperty(nodeId)) {
          updateArray.push($scope.allNodes[nodeId]);
        }
      }
      $scope.nodes.update(updateArray);
    }


    $scope.clusterByCid = function(){
      //network.setData(data);
      var clusterOptionsByData = {
        joinCondition:function(childOptions) {
            return childOptions.com == 1;
        },
        clusterNodeProperties: {id:'cidCluster', borderWidth:3, shape:'dot'}
      }
      $scope.network.cluster(clusterOptionsByData);
    };


    // make the clusters
     $scope.makeClusters = function(scale) {
         var clusterOptionsByData = {
             processProperties: function (clusterOptions, childNodes) {
                 $scope.clusterIndex = $scope.clusterIndex + 1;
                 var childrenCount = 0;
                 for (var i = 0; i < childNodes.length; i++) {
                     childrenCount += childNodes[i].childrenCount || 1;
                 }
                 clusterOptions.childrenCount = childrenCount;
                 clusterOptions.label = "# " + childrenCount + "";
                 clusterOptions.font = {size: childrenCount*5+30}
                 clusterOptions.id = 'cluster:' + $scope.clusterIndex;
                 $scope.cluster.clusters.push({id:'cluster:' + $scope.clusterIndex, scale:scale});
                 return clusterOptions;
             },
             clusterNodeProperties: {borderWidth: 3, shape: 'dot', font: {size: 30}}
         }
         $scope.network.clusterOutliers(clusterOptionsByData);
         $scope.network.setOptions({physics:{stabilization:{fit: false}}});
         $scope.network.stabilize();
     };

     // open them back up!
     $scope.openClusters = function(scale) {
         var newClusters = [];
         var declustered = false;
         for (var i = 0; i < $scope.cluster.clusters.length; i++) {
             if ($scope.cluster.clusters[i].scale < scale) {
                 $scope.network.openCluster($scope.cluster.clusters[i].id);
                 lastClusterZoomLevel = scale;
                 declustered = true;
             }
             else {
                 newClusters.push($scope.cluster.clusters[i])
             }
         }
         $scope.cluster.clusters = newClusters;
         if (declustered === true) {
             // since we use the scale as a unique identifier, we do NOT want to fit after the stabilization
             $scope.network.setOptions({physics:{stabilization:{fit: false}}});
             $scope.network.stabilize();
         }
     };


     $scope.ClusterHighlight = function(nodeList) {
       // if something is selected:
         var i,j,k;
         var selectedNode = 123;//params.nodes[0];

         $scope.info.highlightActive = true;

         var degrees = 2;

         // mark all nodes as hard to read.
         for (var nodeId in $scope.allNodes) {
           $scope.allNodes[nodeId].color = 'rgba(200,200,200,0.5)';
           if ($scope.allNodes[nodeId].hiddenLabel === undefined) {
             $scope.allNodes[nodeId].hiddenLabel = $scope.allNodes[nodeId].label;
             $scope.allNodes[nodeId].label = undefined;
           }
         }


         for(k=0;k<nodeList.length;k++){
           var connectedNodes = $scope.network.getConnectedNodes(nodeList[k]);
           var allConnectedNodes = [];

           // get the second degree nodes
           for (i = 1; i < degrees; i++) {
             for (j = 0; j < connectedNodes.length; j++) {
               allConnectedNodes = allConnectedNodes.concat($scope.network.getConnectedNodes(connectedNodes[j]));
             }
           }

           // all second degree nodes get a different color and their label back
           for (i = 0; i < allConnectedNodes.length; i++) {
             if(nodeList.indexOf(allConnectedNodes[i]) < 0){
               $scope.allNodes[allConnectedNodes[i]].color = 'rgba(150,150,150,0.75)';
               if ($scope.allNodes[allConnectedNodes[i]].hiddenLabel !== undefined) {
                 $scope.allNodes[allConnectedNodes[i]].label = $scope.allNodes[allConnectedNodes[i]].hiddenLabel;
                 $scope.allNodes[allConnectedNodes[i]].hiddenLabel = undefined;
               }
             }
           }

           // all first degree nodes get their own color and their label back
           for (i = 0; i < connectedNodes.length; i++) {
             $scope.allNodes[connectedNodes[i]].color = undefined;
             if ($scope.allNodes[connectedNodes[i]].hiddenLabel !== undefined) {
               $scope.allNodes[connectedNodes[i]].label = $scope.allNodes[connectedNodes[i]].hiddenLabel;
               $scope.allNodes[connectedNodes[i]].color = $scope.allNodes[connectedNodes[i]].permaColor;
               $scope.allNodes[connectedNodes[i]].hiddenLabel = undefined;
             }
           }

           // the main node gets its own color and its label back.
           $scope.allNodes[nodeList[k]].color = $scope.allNodes[nodeList[k]].permaColor;
           if ($scope.allNodes[nodeList[k]].hiddenLabel !== undefined) {
             $scope.allNodes[nodeList[k]].label = $scope.allNodes[nodeList[k]].hiddenLabel;
             $scope.allNodes[nodeList[k]].color = $scope.allNodes[nodeList[k]].permaColor;
             $scope.allNodes[nodeList[k]].hiddenLabel = undefined;
           }
         }




       // transform the object into an array
       var updateArray = [];
       for (nodeId in $scope.allNodes) {
         if ($scope.allNodes.hasOwnProperty(nodeId)) {
           updateArray.push($scope.allNodes[nodeId]);
         }
       }
       $scope.nodes.update(updateArray);
     }




});

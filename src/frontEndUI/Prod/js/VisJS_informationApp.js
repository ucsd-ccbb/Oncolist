
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

app.controller('myCtrl', function ($scope, $http, $log, $filter, HttpServiceJsonp, $location, $timeout) {
  //$scope.pythonHost = "http://localhost:8182"; // Localhost
        //$scope.pythonHost = "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com"; // PROD
  //$scope.pythonHost = "http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com"; //Search Engine (Dev)
  //$scope.pythonHost = "http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:8181"; //Search Engine (Prod)
  $scope.pythonHost = python_host_global;
  console.log("REST services endpoint (VisJS_informationApp): " + $scope.pythonHost);


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
    "selectedClusterColor": "blank"
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
  $scope.nodes;
  $scope.node2;
  $scope.nodeg;
  $scope.circle;
  $scope.w;
  $scope.h;
  $scope.nominal_stroke;
  $scope.allNodes;
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

    $scope.init_page = function(){ //http://localhost:63343/Prototype2/prototype2C.html#?savedId=563a8343f6f4071f79300231
      var termId = GetQueryStringParams('termId');
      $scope.geneList = GetQueryStringParams('geneList');
      var bp_network_title = GetQueryStringParams('networkTitle');
      bp_network_title = bp_network_title.replace("%20", " ");

      // create a DataSet
      $("#selectAuthor").val("-1");

      var options = {};
      var vizOptions = {
          nodes: {
              shape: 'dot',
              size: 16
          },
          edges:{
            "smooth": {
                  "type": "straightCross",
                  "forceDirection": "none",
                  "roundness": 0
                }

          },
          layout: {
            improvedLayout:false,
            randomSeed:2
          },
          physics: {
                forceAtlas2Based: {

                  /*
                  gravitationalConstant: -100,
                   centralGravity: 0.01,
                   springConstant: 0.08,
                   springLength: 100,
                   damping: 0.7,
                   avoidOverlap: 0.5


                    gravitationalConstant: -26,
                    centralGravity: 0.005,
                    springLength: 230,
                    springConstant: 0.18
                    */

                    gravitationalConstant: -65,
                    centralGravity: 0.02,
                    springLength: 130,
                    springConstant: 0.28



                },
                maxVelocity: 16,
                minVelocity: 15,
                solver: 'forceAtlas2Based',
                timestep: 0.27,
                stabilization: true

            }
          };

      var data = new vis.DataSet(options);
      $('#heatmapIsLoading').html('<span class="fa fa-spinner fa-2x fa-pulse"></span>');
      var url = $scope.pythonHost + "/ds/getbpnet/" + $scope.geneList + "?callback=JSON_CALLBACK";
      var myrequest = HttpServiceJsonp.jsonp(url)
           .success(function (result) {
             //alert("Author Gene bp network");
             //$('#heatmap').html('');

             //$scope.w = window.innerWidth - 50,  //800,
             //$scope.h = window.innerHeight - 50;  //600,

             $scope.w = (window.innerWidth > 0) ? window.innerWidth : screen.width;
             $scope.h = (window.innerHeight > 0) ? window.innerHeight : screen.height;  //600,

             $scope.w = $scope.w - 20;
             $scope.h = $scope.h - 60;

             if($scope.w < 780){
               $scope.h -= 80;
             }

             $('#heatmap').width($scope.w);
             $('#heatmap').height($scope.h);

             var nodeArray = [];
             var geneColorArray = [];
             for(var i=0; i<result.nodes.length; i++){
               //gbString = 'rgb(0,127,127.2)'
               rgbString = 'rgb(' + Math.floor(result.nodes[i].rfrac) + ',' + Math.floor(result.nodes[i].gfrac) + ',' + Math.floor(result.nodes[i].bfrac) + ')'
               if($scope.geneList.indexOf(result.nodes[i].id) > -1) {
                 nodeArray.push({id: i, label: result.nodes[i].id, permaLabel: result.nodes[i].id, color: rgbString, permaColor: rgbString, shape: 'square', size: 22});
                 $scope.dropdownGeneNodes.push({id: i, label: result.nodes[i].id, color: rgbString});
                 geneColorArray.push(rgbString);
               } else {
                 nodeArray.push({id: i, label: result.nodes[i].id, color: rgbString, permaColor: rgbString, shape: 'dot'});
                 $scope.dropdownAuthorNodes.push({id: i, label: result.nodes[i].id});
                 //nodeArray.push({id: i, label: rgbString, color: rgbString});
                 //console.log("{id: ", i,", label: '", result.nodes[i].id,"' , color: ", rgbString, "}");
               }
             }

            //=============================
            // GROUP GENES BY CLUSTER
            //=============================
            var geneClust = {};

            geneColorArray.map( function (a) { if (a in geneClust) geneClust[a] ++; else geneClust[a] = 1; } );

            for (var key in geneClust) {
              $scope.ClusterByColor.push({color: key, count: geneClust[key]});
            }
            //=============================
            // END GROUP GENES BY CLUSTER
            //=============================

             var edgeArray = [];

             for(var i=0; i<result.links.length; i++){
               edgeArray.push({from: result.links[i].source, to: result.links[i].target});
               //console.log("{from: ", result.links[i].source,", to: ", result.links[i].target,"}");
             }

             $scope.nodes = new vis.DataSet(nodeArray);
             var edges = new vis.DataSet(edgeArray);

             // create a network
             var container = document.getElementById('heatmap');
             var data = {
               nodes: $scope.nodes,
               edges: edges
             };
             var options = {};
             $scope.network = new vis.Network(container, data, vizOptions);


             $scope.allNodes = $scope.nodes.get({returnType:"Object"});

             $scope.network.fit();
             $scope.network.on("click",neighbourhoodHighlight);

             $scope.network.on("oncontext", function (params) {
               //params.event.preventDefault();
                $('#eventSpan').html('context clicked');
                //document.getElementById('eventSpan').innerHTML = '<h3>Starting Stabilization</h3>';
                console.log("context")
              });


              //===========================
              // ZOOM CLUSTERING
              //===========================
              // set the first initial zoom level
              /*
              $scope.network.once('initRedraw', function() {
                  if ($scope.lastClusterZoomLevel === 0) {
                      $scope.lastClusterZoomLevel = $scope.network.getScale();
                  }
              });


              // we use the zoom event for our clustering
              $scope.network.on('zoom', function (params) {
                  if (params.direction == '-') {
                      if (params.scale < $scope.lastClusterZoomLevel * $scope.clusterFactor) {
                          $scope.makeClusters(params.scale);
                          $scope.lastClusterZoomLevel = params.scale;
                      }
                  }
                  else {
                      $scope.openClusters(params.scale);
                  }
              });
              */
              //===========================
              // END ZOOM CLUSTERING
              //===========================


/*
             $scope.network.on("startStabilizing", function (params) {
                $('#eventSpan').html('<h3>Starting Stabilization</h3>');
                //document.getElementById('eventSpan').innerHTML = '<h3>Starting Stabilization</h3>';
                console.log("started")
              });
              $scope.network.on("stabilizationProgress", function (params) {
                $('#eventSpan').html('<h3>Stabilization progress</h3>' + JSON.stringify(params, null, 4));
                //document.getElementById('eventSpan').innerHTML = '<h3>Stabilization progress</h3>' + JSON.stringify(params, null, 4);
                console.log("progress:",params);
              });
              $scope.network.on("stabilizationIterationsDone", function (params) {
                $('#eventSpan').html('<h3>Stabilization iterations complete</h3>');
                //document.getElementById('eventSpan').innerHTML = '<h3>Stabilization iterations complete</h3>';
                console.log("finished stabilization interations");
              });
              $scope.network.on("stabilized", function (params) {
                $('#eventSpan').html('<h3>Stabilized!</h3>' + JSON.stringify(params, null, 4));
                //document.getElementById('eventSpan').innerHTML = '<h3>Stabilized!</h3>' + JSON.stringify(params, null, 4);
                console.log("stabilized!", params);
              });
*/

             $timeout(function() {
               $('#heatmapIsLoading').html('');
             }, 1000);

           }).finally(function () {
      }).error(function (data, status, headers, config) {
                    alert(data + ' - ' + status + ' - ' + headers);
      });

    };

    function neighbourhoodHighlight(params) {
      // if something is selected:
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

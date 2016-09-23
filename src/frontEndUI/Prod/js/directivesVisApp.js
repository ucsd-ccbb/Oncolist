var app = angular.module('myApp'); //ui-bootstrap

var useLocalHost = false;

var cy;

var historySize = 0;

/*
==========================================
==========================================
        NETWORK VIS
        DIRECTIVE
==========================================
==========================================
*/
app.directive('visJsGraph', function (HttpServiceJsonp, $timeout) {
    function link(scope, el, attrs) {

        scope.pythonHost = python_host_global;
        //scope.pythonHost = "http://localhost:8182"; // Localhost

      scope.info = {"TermId": "",
        "searchTerms": "",
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
        "clusterId": "",
        "nodeSizeToggleState": true,
        "doneRendering": false,
        "legendDoneRendering": false,
        "legendReady": false,
        "geneListArray": [],
        "filterValue": 0,
        "dragStartY": 90,
        "nodeValueType": "EXPRESSION",
        "isNode": true,
        "annotations": [],
        "go_genes": {},
        "annotationChecked": "NONE"
      };
      scope.showMore = {
        "origin": "modalWindow",
        shapeDescriptions: false,
        annotations: false,
        colors: false
      };

      scope.minRangeSlider = {
         minValue: 0,
         maxValue: 100,
         options: {
           floor: 0,
           ceil: 100,
           step: 1,
           minRange: 0,
           maxRange: 100
         }
       };

       $timeout(function() {
           scope.$broadcast('rzSliderForceRender');
           //scope.init_page();
           console.log("range slider init");
      }, 4000);



      scope.rangeOutput = {
          "expression": 0,
          "localcc": 0,
          "edgeWeight": 0
      };

    scope.$watch('rangeOutput.expression', function() {
        for (var nodeId in scope.allNodes) {
          if(parseFloat(scope.rangeOutput.expression) == 0.0){
              scope.allNodes[nodeId].color.borderWidth = 1;
              scope.allNodes[nodeId].size = scope.allNodes[nodeId].permaSize;

          }
          else if (scope.allNodes[nodeId].node_value >= (parseFloat(scope.rangeOutput.expression) - 0.1)){
              scope.allNodes[nodeId].hidden = false;

              var connectedEdges = scope.network.getConnectedEdges(nodeId);

              for (i = 0; i < connectedEdges.length; i++) {
                  // only display the edge if both source and target nodes are visible
                  if((!scope.allNodes[scope.allEdges[connectedEdges[i]].from].hidden) && (!scope.allNodes[scope.allEdges[connectedEdges[i]].to].hidden)){
                      scope.allEdges[connectedEdges[i]].hidden = false;
                  }
              }
          } else if(!scope.allNodes[nodeId].hidden){

              var connectedEdges = scope.network.getConnectedEdges(nodeId);
              for (i = 0; i < connectedEdges.length; i++) {
                  scope.allEdges[connectedEdges[i]].hidden = true;
              }
              scope.allNodes[nodeId].hidden = true;
          }
        }

        // transform the object into an array
        var updateEdgeArray = [];
        for (edgeId in scope.allEdges) {
          if (scope.allEdges.hasOwnProperty(edgeId)) {
            updateEdgeArray.push(scope.allEdges[edgeId]);
          }
        }

        if(scope.edges){
            scope.edges.update(updateEdgeArray);
        }

        var updateArray = [];
        for (nodeId in scope.allNodes) {
            if (scope.allNodes.hasOwnProperty(nodeId)) {
              updateArray.push(scope.allNodes[nodeId]);
            }
        }

        if(scope.nodes){
          scope.nodes.update(updateArray);
        }
    });

    scope.$watch('rangeOutput.localcc', function() {
        for (var nodeId in scope.allNodes) {
            if(parseFloat(scope.rangeOutput.localcc) == 0.0){
                scope.allNodes[nodeId].color.borderWidth = 1;
                scope.allNodes[nodeId].size = scope.allNodes[nodeId].permaSize;

            }
            else if (scope.allNodes[nodeId].local_cc >= (parseFloat(scope.rangeOutput.localcc) - 0.1)){
                scope.allNodes[nodeId].hidden = false;

                var connectedEdges = scope.network.getConnectedEdges(nodeId);

                for (i = 0; i < connectedEdges.length; i++) {
                    // only display the edge if both source and target nodes are visible
                    if((!scope.allNodes[scope.allEdges[connectedEdges[i]].from].hidden) && (!scope.allNodes[scope.allEdges[connectedEdges[i]].to].hidden)){
                        scope.allEdges[connectedEdges[i]].hidden = false;
                    }
                }
            } else if(!scope.allNodes[nodeId].hidden){

                var connectedEdges = scope.network.getConnectedEdges(nodeId);
                for (i = 0; i < connectedEdges.length; i++) {
                    scope.allEdges[connectedEdges[i]].hidden = true;
                }
                scope.allNodes[nodeId].hidden = true;
            }
        }

        // transform the object into an array
        var updateEdgeArray = [];
        for (edgeId in scope.allEdges) {
          if (scope.allEdges.hasOwnProperty(edgeId)) {
            updateEdgeArray.push(scope.allEdges[edgeId]);
          }
        }

        if(scope.edges){
            scope.edges.update(updateEdgeArray);
        }

        var updateArray = [];
        for (nodeId in scope.allNodes) {
          if (scope.allNodes.hasOwnProperty(nodeId)) {
            updateArray.push(scope.allNodes[nodeId]);
          }
        }

        if(scope.nodes){
            scope.nodes.update(updateArray);
        }

  });

    scope.$watch('rangeOutput.edgeWeight', function() {
        for (var edgeId in scope.allEdges) {
            if(scope.allEdges[edgeId].edgeWeight <= (parseFloat(scope.rangeOutput.edgeWeight) - 0.001)){
                scope.allEdges[edgeId].hidden = true;

                //get the nodes connected to this edge
                var toNodeId = scope.allEdges[edgeId].to;
                var fromNodeId = scope.allEdges[edgeId].from;

                //check the edges of the node
                var okToHide = true;
                var toConnectedEdges = scope.network.getConnectedEdges(toNodeId);
                for (i = 0; i < toConnectedEdges.length; i++) {
                    if(toConnectedEdges[i] != edgeId){
                        if(!scope.allEdges[toConnectedEdges[i]].hidden){
                            okToHide = false;
                        }
                    }
                }

                //If all of the edges are hidden then hide the node
                if(okToHide){
                    scope.allNodes[toNodeId].hidden = true;
                }

                okToHide = true;
                var fromConnectedEdges = scope.network.getConnectedEdges(fromNodeId);
                for (i = 0; i < fromConnectedEdges.length; i++) {
                    if(fromConnectedEdges[i] != edgeId){
                        if(!scope.allEdges[fromConnectedEdges[i]].hidden){
                            okToHide = false;
                        }
                    }
                }

                //If all of the edges are hidden then hide the node
                if(okToHide){
                    scope.allNodes[fromNodeId].hidden = true;
                }
            } else {
                var toNodeId = scope.allEdges[edgeId].to;
                var fromNodeId = scope.allEdges[edgeId].from;
                scope.allNodes[toNodeId].hidden = false;
                scope.allNodes[fromNodeId].hidden = false;
                scope.allEdges[edgeId].hidden = false;
            }
        }
        // transform the object into an array
        var updateNodeArray = [];
        for (nodeId in scope.allNodes) {
          if (scope.allNodes.hasOwnProperty(nodeId)) {
            updateNodeArray.push(scope.allNodes[nodeId]);
          }
        }

        if(scope.nodes){
            scope.nodes.update(updateNodeArray);
        }

        var updateArray = [];
        for (edgeId in scope.allEdges) {
          if (scope.allEdges.hasOwnProperty(edgeId)) {
            updateArray.push(scope.allEdges[edgeId]);
          }
        }
        if(scope.edges){
            scope.edges.update(updateArray);
        }
  });

    scope.reorderNodes = function(){
        var gravConstant = (Math.floor(Math.random() * 8000) + 1 ) * -1;
        var randSpringLength = Math.floor(Math.random() * 100) + 50;
        var options = {
          nodes: {
              borderWidth: 1,
              shape: 'dot',
              font: {
                size: 20,
                face: 'Tahoma'
              },
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
              size: 16
          },
          edges:{
            width: 0.15,
            smooth: {
              "type": "continuous",
              "forceDirection": "none",
              "roundness": 0.15
            },
            physics: true

          },
          layout: {
              improvedLayout:true,
              hierarchical: {
                enabled:false,
                levelSeparation: 150,
                direction: 'UD',   // UD, DU, LR, RL
                sortMethod: 'hubsize' // hubsize, directed
              },
              randomSeed:780555
          },
          interaction:{
            hideEdgesOnDrag: true,
            hover:true,
            tooltipDelay: 300
          },
          physics: {
            stabilization: false,
            barnesHut: {gravitationalConstant: gravConstant, springConstant: 0.112, springLength: randSpringLength},
            //barnesHut: {gravitationalConstant: -3000, springConstant: 0.011, springLength: 100},
            //repulsion: {centralGravity: 0.2, springLength: 200, springConstant: 0.005, nodeDistance: 100, damping: 0.29},
            //hierarchicalRepulsion: {centralGravity: 0.0,springLength: 100,springConstant: 0.01,nodeDistance: 120,damping: 0.09},
            //forceAtlas2Based: {gravitationalConstant: -65, centralGravity: 0.02, springLength: 130, springConstant: 0.28, avoidOverlap: 0.2},
            maxVelocity: 8,
            minVelocity: 5,
            solver: 'barnesHut',
            adaptiveTimestep: true,
            stabilization: {
              enabled: true,
              iterations: 1000,
              updateInterval: 100,
              onlyDynamicEdges: false,
              fit: true
            }

          }
        };

        scope.network.setOptions(options);


/*
var options = {
  configure: {
    enabled: true,
    filter: 'physics',
    container: undefined,
    showButton: true
  }
}

scope.network.redraw();

        for (var nodeId in scope.allNodes) {
            if(goGenes.indexOf(scope.allNodes[nodeId].label) > -1){
                scope.allNodes[nodeId].color = "#00FF00";
                scope.allNodes[nodeId].font.size = 40;
            } else {
                scope.allNodes[nodeId].color = "rgba(150,150,150,0.75)";
                scope.allNodes[nodeId].font.size = scope.allNodes[nodeId].permaFont.size;

            }

        }

        var updateArray = [];
        for (nodeId in scope.allNodes) {
          if (scope.allNodes.hasOwnProperty(nodeId)) {
            updateArray.push(scope.allNodes[nodeId]);
          }
        }
        scope.nodes.update(updateArray);
        */
    };

  scope.getAnnotationGenes = function(GO_id){
      if(scope.info.go_genes.hasOwnProperty(GO_id)){
          console.log("Already have this GOID");
          scope.highlightGoGenes(GO_id);
      } else {
          var url = scope.pythonHost + "/api/go/genes/" + GO_id + "?callback=JSON_CALLBACK";
          var myrequest = HttpServiceJsonp.jsonp(url)
          .success(function (result) {
              scope.info.go_genes[GO_id] = result;
              scope.highlightGoGenes(GO_id);
          }).finally(function () {
          }).error(function (data, status, headers, config) {
              alert(data + ' - ' + status + ' - ' + headers);
          });
      }
  }

  scope.clearLegendHighlight = function(){
        scope.rangeOutput.edgeWeight = 0;
        scope.rangeOutput.expression = 0;
        scope.rangeOutput.localcc = 0;
        scope.info.annotationChecked = "NONE";
        scope.info.highlightActive = true;
        scope.neighborhoodHighlight({'nodes': []});
  };
      scope.d3root;
      scope.geneList;
      scope.svg;
      scope.zoom;
      scope.force;
      scope.fisheye;
      scope.d3link;
      scope.d3link2;
      scope.node;
      scope.result;
      scope.nodes;
      scope.edges;
      scope.node2;
      scope.nodeg;
      scope.circle;
      scope.w;
      scope.h;
      scope.nominal_stroke;
      scope.allNodes;
      scope.allEdges;
      scope.network;
      scope.item;
      scope.dropdownAuthorNodes = [];
      scope.dropdownGeneNodes = [];
      scope.ClusterByColor = [];
      scope.lastClusterZoomLevel = 0;
      scope.clusterFactor = 0.9;
      scope.clusterIndex = 0;
      scope.cluster = {
        "clusters": [],
        "filterMessage": ""
      };

        var termId = "";//GetQueryStringParams('termId');
        scope.geneList = scope.overlapGeneList;
        if(scope.info.geneListArray.length > 0){
            scope.info.geneListArray = scope.geneList.split(',');
        } else {
            scope.info.geneListArray = ['INVALIDGENE'];
            scope.geneList = "INVALIDGENE";
        }

        var bp_network_title = "";//GetQueryStringParams('networkTitle');
        bp_network_title = bp_network_title.replace("%20", " ");
        scope.info.clusterId = "2020014839";//GetQueryStringParams("clusterId");

        $('#modalTitle').html(scope.clusterTitle);
        console.log(scope.clusterTitle);

        scope.showMore.origin = "";//GetQueryStringParams("origin");

        $('#heatmapIsLoading').html('<span class="fa fa-spinner fa-2x fa-pulse"></span>');

        var url = "";
        if(scope.heatOverlapNodes){
            if(scope.heatOverlapNodes.length > 0){
                heatGenes = [];
                var searchTermsTemp = [];
                for(var i=0; i<scope.heatOverlapNodes.length;i++){
                    heatGenes.push(scope.heatOverlapNodes[i].gene);
                }

                for(var i=0; i<scope.overlapGeneList.length;i++){
                    //console.log(scope.overlapGeneList[i].gene);
                    if(scope.overlapGeneList[i].type === "gene"){
                        searchTermsTemp.push(scope.overlapGeneList[i].user);
                        if(heatGenes.indexOf(scope.overlapGeneList[i].user) < 0){
                            heatGenes.push(scope.overlapGeneList[i].user);
                        }
                    }
                }

                var heatGenesList = heatGenes.join(",");
                scope.info.searchTerms = searchTermsTemp.join(",");

                url = scope.pythonHost + "/ds/getheatmapgraph/" + scope.clusterId + "/" + heatGenesList + "/200?callback=JSON_CALLBACK";
            }
        } else {
            url = scope.pythonHost + "/ds/getheatmapgraph/" + scope.clusterId + "/" + scope.overlapGeneList + "/200?callback=JSON_CALLBACK";
        }
        var myrequest = HttpServiceJsonp.jsonp(url)
        .success(function (result) {
            scope.result = result;
            scope.cluster.filterMessage = result.filter_message;
            scope.w = (window.innerWidth > 0) ? window.innerWidth : screen.width;
            scope.h = (window.innerHeight > 0) ? window.innerHeight + 30 : screen.height + 30;  //600,

            scope.w = scope.w - 0;
            scope.h = scope.h - 60;

            var nodeArray = [];
            var geneColorArray = [];
            var colorCcDict = {};
            //onsole.log(result.nodes);
            scope.info.annotations = result.annotations;
            for(var i=0; i<result.nodes.length; i++){
                   var expressionRGBString = "";
                 //gbString = 'rgb(0,127,127.2)'

                 //var scale = chroma.scale(['blue', 'white', 'red']);
                 var scaleHeatProp = chroma.scale(['#FFF7EB','800C00']); //BROWN
                 var scale = chroma.scale(['#7AFFFF','FF00FF']); //Turquoise

                 clusterRGBString = 'rgb(' + Math.floor(result.nodes[i].rfrac) + ',' + Math.floor(result.nodes[i].gfrac) + ',' + Math.floor(result.nodes[i].bfrac) + ')'

                 expressionRGBString = scale(result.nodes[i].expression_value).hex()

                 var l_cc = result.nodes[i].local_cc
                 colorCcDict[expressionRGBString] = l_cc;

                 var node_degree = result.nodes[i].degree > 30 ? 30 + ((result.nodes[i].degree - 30)/6) : result.nodes[i].degree;
                 node_degree = Math.sqrt(node_degree) * 2;
                 node_degree = node_degree > 50 ? 50 : node_degree;
                 node_degree = node_degree < 4 ? 4 : node_degree;
                 var font_size = result.nodes[i].degree * 3;
                 font_size = font_size < 10 ? 10 : font_size;
                 var node_shape = "dot";

                 var id_clean = result.nodes[i].id.replace("_g","").replace("_v","").replace("_m","");
                 if(result.nodes[i].id.substring(result.nodes[i].id.length - 2, result.nodes[i].id.length) === "_g"){
                     node_shape = "dot";
                 } else if (result.nodes[i].id.substring(result.nodes[i].id.length - 2, result.nodes[i].id.length) === "_v") {
                     node_shape = "diamond";
                 } else if (result.nodes[i].id.substring(result.nodes[i].id.length - 2, result.nodes[i].id.length) === "_m") {
                     node_shape = "triangle";
                 }

                 if(scope.heatOverlapNodes){
                      if(scope.heatOverlapNodes.length > 0){
                          console.log("id_clean: " + id_clean);
                          for(var j=0;j<scope.heatOverlapNodes.length;j++){
                              if(id_clean === "STK39"){
                                  var myStr = "";
                              }
                              if(scope.heatOverlapNodes[j].gene === id_clean){
                                  expressionRGBString = scaleHeatProp(scope.heatOverlapNodes[j].normalized_heat).hex();
                                  //id_clean = id_clean + ": " + scope.heatOverlapNodes[j].normalized_heat.toString();
                              }
                          }
                      }
                  }

                  scope.title = "<div class='panel panel-success' style='margin-bottom:0px'>"+
                  			"<div class='panel-heading'>"+
                  				"<h3 class='panel-title'>Agent</h3>"+
                  			"</div>"+
                  			"<div class='panel-body' style='height: 145px; padding-top: 0px; padding-bottom: 0px'>"+
                  				"<table class='table' style='border: none; margin-bottom:1px'>"+
                  					"<tr>"+
                  						"<td>Agent</td>"+
                  						"<td>true</td>"+
                  						"<td>2015-04-02 16:02</td>"+
                  					"</tr>"+
                  					"<tr>"+
                  						"<td>CPU</td>"+
                  						"<td>1%</td>"+
                  						"<td>2015-04-02 16:02</td>"+
                  					"</tr>"+
                  					"<tr>"+
                  						"<td>Memory</td>"+
                  						"<td>2%</td>"+
                  						"<td>2015-04-02 16:02</td>"+
                  					"</tr>"+
                  					"<tr>"+
                  						"<td>Disk</td>"+
                  						"<td>10%</td>"+
                  						"<td>2015-04-02 16:02</td>"+
                  					"</tr>"+
                  				"</table>"+
                  			"</div>"+
                  		"</div>";

                if(typeof scope.heatDrugGenes != 'undefined'){
                    if(scope.heatDrugGenes.indexOf(result.nodes[i].id.replace("_g","").replace("_v","").replace("_m","")) > -1) {
                        geneColorArray.push(expressionRGBString + "query");
                        nodeArray.push({id: i, label: id_clean, title: "scope.title", 'node_value': result.nodes[i].expression_value, permaFont: {size: font_size}, font: {size: 20}, permaLabel: id_clean, borderWidth: 4,
                        color: {'background': expressionRGBString, 'border': '#FF0000'}, permaColor: {'background':expressionRGBString, 'border': '#0000FF'},
                        expressionRGB: expressionRGBString, clusterRGB: clusterRGBString,
                        local_cc: result.nodes[i].local_cc,
                        shape: "square", size: 20, permaSize: 20, nodeDegree: 20});
                        scope.dropdownGeneNodes.push({id: i, label: result.nodes[i].id, color: expressionRGBString});
                    } else {
                        geneColorArray.push(expressionRGBString);
                        nodeArray.push({id: i, label: id_clean, permaLabel: id_clean, title: "scope.title", 'node_value': result.nodes[i].expression_value, permaFont: {size: font_size}, font: {size: font_size},
                        color: {'background':expressionRGBString, 'border': '#c0c0c0'},
                        expressionRGB: expressionRGBString, clusterRGB: clusterRGBString,
                        local_cc: result.nodes[i].local_cc,
                        permaColor: {'background':expressionRGBString, 'border': '#c0c0c0'},
                        shape: node_shape, size: 20, permaSize: 20, nodeDegree: node_degree});
                        scope.dropdownAuthorNodes.push({id: i, label: result.nodes[i].id});
                    }
                } else if(scope.geneList.indexOf(result.nodes[i].id.replace("_g","").replace("_v","").replace("_m","")) > -1) {
                    geneColorArray.push(expressionRGBString + "query");
                    nodeArray.push({id: i, label: id_clean, title: "scope.title", 'node_value': result.nodes[i].expression_value, permaFont: {size: font_size}, font: {size: 20}, permaLabel: id_clean, borderWidth: 4,
                    color: {'background': expressionRGBString, 'border': '#FF0000'}, permaColor: {'background':expressionRGBString, 'border': '#0000FF'},
                    expressionRGB: expressionRGBString, clusterRGB: clusterRGBString,
                    local_cc: result.nodes[i].local_cc,
                    shape: "square", size: 20, permaSize: 20, nodeDegree: 20});
                    scope.dropdownGeneNodes.push({id: i, label: result.nodes[i].id, color: expressionRGBString});
                } else {
                    geneColorArray.push(expressionRGBString);
                    nodeArray.push({id: i, label: id_clean, permaLabel: id_clean, title: "scope.title", 'node_value': result.nodes[i].expression_value, permaFont: {size: font_size}, font: {size: font_size},
                    color: {'background':expressionRGBString, 'border': '#c0c0c0'},
                    expressionRGB: expressionRGBString, clusterRGB: clusterRGBString,
                    local_cc: result.nodes[i].local_cc,
                    permaColor: {'background':expressionRGBString, 'border': '#c0c0c0'},
                    shape: node_shape, size: 20, permaSize: 20, nodeDegree: node_degree});
                    scope.dropdownAuthorNodes.push({id: i, label: result.nodes[i].id});
                }

            }

               //=============================
               //=============================
               //=============================
               // LEGEND
               // GROUP GENES BY CLUSTER
               //=============================
               //=============================
               //=============================

               //=============================
               // END GROUP GENES BY CLUSTER
               //=============================

               var edgeArray = [];

               var scale = chroma.scale(['blue', 'white', 'red']).domain([-1.0, 1.0]);

               for(var i=0; i<result.links.length; i++){
                 edgeArray.push({from: result.links[i].source, to: result.links[i].target, label: '',
                    font: {align: 'horizontal', size: 20, background: 'rgba(255,255,255,255)'},
                    title: result.links[i].weight, zindex: 1050,
                    edgeWeight: result.links[i].weight,
                    color: {
                        color: scale(result.links[i].weight + 0.1).hex(),
                        hover: scale(result.links[i].weight + 0.15).hex(),
                        highlight: scale(result.links[i].weight + 0.15).hex(),
                        opacity: (0.6)//Math.abs(result.links[i].weight) - 0.15)
                    },
                    permaColor: {
                        color: scale(result.links[i].weight + 0.1).hex(),
                        hover: scale(result.links[i].weight + 0.15).hex(),
                        highlight: scale(result.links[i].weight + 0.15).hex(),
                        opacity: (Math.abs(result.links[i].weight) - 0.15)
                    },
                    hidden: false
                   }
                 );
               }

                scope.nodes = new vis.DataSet(nodeArray);
                scope.edges = new vis.DataSet(edgeArray);

                scope.nodeArray = nodeArray;
                scope.edgeArray = edgeArray;

                // create a network
                var container = document.getElementById('heatmap');
                var data = {
                  edges: scope.edges,
                  nodes: scope.nodes
                };
                var options = {
                  nodes: {
                      borderWidth: 1,
                      shape: 'dot',
                      font: {
                        size: 20,
                        face: 'Tahoma'
                      },
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
                      size: 16
                  },
                  edges:{
                    width: 1.0,
                    smooth: {
                      "type": "continuous",
                      "forceDirection": "none",
                      "roundness": 0.15
                    },
                    physics: true

                  },
                  layout: {
                      improvedLayout:true,
                      hierarchical: {
                        enabled:false,
                        levelSeparation: 150,
                        direction: 'UD',   // UD, DU, LR, RL
                        sortMethod: 'hubsize' // hubsize, directed
                      },
                      randomSeed:780555
                  },
                  interaction:{
                    hideEdgesOnDrag: true,
                    hover:true,
                    tooltipDelay: 300
                  },
                  physics: {
                    stabilization: true,
                    barnesHut: {gravitationalConstant: -8000, springConstant: 0.012, springLength: 100},
                    maxVelocity: 8,
                    minVelocity: 5,
                    solver: 'barnesHut',
                    adaptiveTimestep: true,
                    stabilization: {
                      enabled: true,
                      iterations: 300,
                      updateInterval: 200,
                      onlyDynamicEdges: false,
                      fit: true
                    }

                  }
                };




                scope.network = new vis.Network(container, data, options);//pre_rendered_options); //vizOptions);

                scope.allNodes = scope.nodes.get({returnType:"Object"});
                scope.allEdges = scope.edges.get({returnType:"Object"});

                scope.network.fit();

                scope.network.on("click",scope.neighborhoodHighlight);

                scope.network.on("hoverEdge", scope.hoverEdge);

                scope.network.on("selectEdge",scope.selectEdge);

                scope.network.on("blurEdge", scope.blurEdge);

                scope.network.on("blurNode", function (params) {
                    //console.log(scope.network.getBoundingBox(params.node));

                    //console.log(params);
                    //scope.allNodes[params.node].title = scope.title;
                    //var updateArray = [];
                    //updateArray.push(scope.allNodes[params.node]);
                    //scope.nodes.update(updateArray);
                });
                scope.network.on("afterDrawing", scope.afterDrawing);

                //scope.network.on("showPopup", function (params) {
                //    scope.title="<h2>changed</h2>";
                //});
               $timeout(function() {
                 $('#heatmapIsLoading').html('');
               }, 500);

             }).finally(function () {
        }).error(function (data, status, headers, config) {
                      alert(data + ' - ' + status + ' - ' + headers);
        });

        scope.focusOnNode = function(focusOnThis){
            var options = {
              animation: {
                duration: 150,
                easingFunction: "linear"
              }
            }

            for (var nodeId in scope.allNodes) {
                if(scope.allNodes[nodeId].label === focusOnThis){
                    //console.log(scope.allNodes[nodeId]);
                    scope.network.focus(scope.allNodes[nodeId].id, options);
                    break;
                }
            }
        };

        scope.re_fit = function() {
            if(scope.legendNetwork != null){
                $timeout(function() {
                    //$scope.info.legendReady = true;
                    scope.legendNetwork.fit();
                }, 200);

            }
        };

        scope.changeNodeValue = function(nodeValueType){
            // mark all nodes as hard to read.
            scope.info.nodeValueType = nodeValueType;
            if(nodeValueType === "CLUSTERINGCOEF"){
                for (var nodeId in scope.allNodes) {
                    scope.allNodes[nodeId].color.background = scope.allNodes[nodeId].clusterRGB;
                }
            } else if(nodeValueType === "EXPRESSION"){
                for (var nodeId in scope.allNodes) {
                  scope.allNodes[nodeId].color.background = scope.allNodes[nodeId].expressionRGB;
                }
            }

            // transform the object into an array
            var updateArray = [];
            for (nodeId in scope.allNodes) {
              if (scope.allNodes.hasOwnProperty(nodeId)) {
                updateArray.push(scope.allNodes[nodeId]);
              }
            }

            scope.nodes.update(updateArray);
        }

        scope.exportData = function(){
          var exportArrayString = "data:text/csv;charset=utf-8,";
          var tempHeader = "NODES\nnode_name,community_id,degree";
          exportArrayString += tempHeader + '\n';

          var tableNodeTempString = "<table id='node-table'>";

          tableNodeTempString += "<thead><tr><th>node_name</th><th>community_id</th><th>degree</th></tr></thead>";

          for (var i = 0; i < scope.result.nodes.length; i++) {
            tableNodeTempString += "<tr><td>" + scope.result.nodes[i]["id"] + "</td><td>" + scope.result.nodes[i]["com"] + "</td><td>" + scope.result.nodes[i]["degree"] + "</td></tr>";
              exportArrayString += "" + scope.result.nodes[i]["id"] + "," + scope.result.nodes[i]["com"] + "," + scope.result.nodes[i]["degree"] + '\n';
          }

          tableNodeTempString += "</table>";

          exportArrayString += '\n\n\n\n\n';

          var tempHeader = "EDGES\nsource,target,weight";

          exportArrayString += tempHeader + '\n';

          var tableEdgeTempString = "<table id='edge-table'>";

          tableEdgeTempString += "<thead><tr><th>source</th><th>target</th><th>weight</th></tr></thead>";

          for (var j = 0; j < scope.result.links.length; j++) {
            tableEdgeTempString += "<tr><td>" + scope.result.links[j]["source"] + "</td><td>" + scope.result.links[j]["target"] + "</td><td>" + scope.result.links[j]["weight"] + "</td></tr>";

              exportArrayString += "" + scope.result.links[j]["source"] + "," + scope.result.links[j]["target"] + "," + scope.result.links[j]["weight"] + '\n';
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
        };

        scope.selectEdge = function(params){
          var selectedNode = params.edges[0];
          // the main node gets its own color and its label back.
          for (var nodeId in scope.allEdges) {
            if (scope.allEdges[nodeId].id === selectedNode) {
              scope.allEdges[nodeId].label = scope.allEdges[nodeId].title;

              var updateArray = [];
              for (nodeId in scope.allEdges) {
                if (scope.allEdges.hasOwnProperty(nodeId)) {
                  updateArray.push(scope.allEdges[nodeId]);
                }
              }
              scope.edges.update(updateArray);
            } else {
              scope.allEdges[nodeId].label = '';
            }
          }
        }

        scope.toggleNodeSize = function(){
            // mark all nodes as hard to read.
            if(scope.info.nodeSizeToggleState){
                for (var nodeId in scope.allNodes) {
                    scope.allNodes[nodeId].size = 20;
                    scope.allNodes[nodeId].color.background = scope.allNodes[nodeId].clusterRGB;
                    //console.log(scope.allNodes[nodeId].clusterRGB);
                    //console.log(scope.allNodes[nodeId].color.background);
                }
            } else {
                for (var nodeId in scope.allNodes) {
                  scope.allNodes[nodeId].size = scope.allNodes[nodeId].permaSize;
                  scope.allNodes[nodeId].color.background = scope.allNodes[nodeId].expressionRGB;
                }
            }

            // transform the object into an array
            var updateArray = [];
            for (nodeId in scope.allNodes) {
              if (scope.allNodes.hasOwnProperty(nodeId)) {
                updateArray.push(scope.allNodes[nodeId]);
              }
            }

            scope.info.nodeSizeToggleState = !scope.info.nodeSizeToggleState;

            scope.nodes.update(updateArray);
        };



        for (var nodeId in scope.allNodes) {
            if(scope.info.nodeValueType === "LOCALCC"){
                scope.allNodes[nodeId].color = scope.allNodes[nodeId].clusterRGB;
            } else {
                scope.allNodes[nodeId].color = scope.allNodes[nodeId].expressionRGB;
            }

          if (scope.allNodes[nodeId].hiddenLabel !== undefined) {
            scope.allNodes[nodeId].label = scope.allNodes[nodeId].hiddenLabel;
            scope.allNodes[nodeId].hiddenLabel = undefined;
          }
        }



        scope.switchNodeColor = function(colorScheme){
            scope.info.nodeValueType = colorScheme;
            if(colorScheme === "LOCALCC"){
                for (var nodeId in scope.allNodes) {
                    scope.allNodes[nodeId].size = 20;
                    scope.allNodes[nodeId].color = scope.allNodes[nodeId].clusterRGB;
                    if (scope.allNodes[nodeId].hiddenLabel !== undefined) {
                      scope.allNodes[nodeId].label = scope.allNodes[nodeId].hiddenLabel;
                      scope.allNodes[nodeId].hiddenLabel = undefined;
                    }
                }
            } else {
                for (var nodeId in scope.allNodes) {
                  scope.allNodes[nodeId].size = scope.allNodes[nodeId].permaSize;
                  scope.allNodes[nodeId].color = scope.allNodes[nodeId].expressionRGB;
                  if (scope.allNodes[nodeId].hiddenLabel !== undefined) {
                    scope.allNodes[nodeId].label = scope.allNodes[nodeId].hiddenLabel;
                    scope.allNodes[nodeId].hiddenLabel = undefined;
                  }
                }
            }

            // transform the object into an array
            var updateArray = [];
            for (nodeId in scope.allNodes) {
              if (scope.allNodes.hasOwnProperty(nodeId)) {
                updateArray.push(scope.allNodes[nodeId]);
              }
            }

            scope.info.nodeSizeToggleState = !scope.info.nodeSizeToggleState;

            scope.nodes.update(updateArray);
        };

        scope.exportRawData = function(){
            $('#heatmapIsLoading').html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="fa fa-spinner fa-2x fa-pulse"></span>');

            var url = scope.pythonHost + "/ds/getrawcluster/" + scope.clusterId + "/" + scope.overlapGeneList + "?callback=JSON_CALLBACK";
            var myrequest = HttpServiceJsonp.jsonp(url)
            .success(function (result) {
                //console.log(result);
                var exportArrayString = "data:text/tsv;charset=utf-8,source\ttarget\tweight\n"; //+ JSON.stringify(result["edges"]);

                for(var i=0; i< result["edges"].length; i++){
                    exportArrayString += result["edges"][i]["source"] + "\t" + result["edges"][i]["target"] + "\t" + result["edges"][i]["weight"] + "\n";
                }

                var encodedUri = encodeURI(exportArrayString);
                $('#heatmapIsLoading').html('');
                window.open(encodedUri);
            }).finally(function () {
            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });
        };

        scope.exportImage = function(){
            $('#heatmapIsLoading').html('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<span class="fa fa-spinner fa-2x fa-pulse"></span>');
            var canvas = document.querySelector("canvas");

            scope.init_w = canvas.width;
            scope.init_h = canvas.height;

            scope.init_window_w = $('#heatmap').width();
            scope.init_window_h = $('#heatmap').height();

            $('#heatmap').width(7000);
            $('#heatmap').height(7000);

            canvas.width = 7000;
            canvas.height = 7000;
            scope.network.fit();


            $timeout(function() {
                $('#heatmapIsLoading').html('');
                var canvas = document.querySelector("canvas");
                var context = canvas.getContext('2d');

                var image = new Image();
                image.src = canvas.toDataURL("image/png");

                var anchor = document.createElement('a');
                context.globalCompositeOperation = "destination-over";

                anchor.setAttribute('download', 'saveIt.png');
                anchor.setAttribute('href', image.src);
                anchor.click();

                $('#heatmap').width(scope.init_window_w);
                $('#heatmap').height(scope.init_window_h);

                canvas.width = scope.init_w;
                canvas.height = scope.init_h;

                scope.network.fit();
                rescale();
            }, 1000);



        };

        scope.hoverEdge = function (params) {
          for (var nodeId in scope.allEdges) {
            if (scope.allEdges[nodeId].id === params["edge"]) {
              scope.allEdges[nodeId].label = scope.allEdges[nodeId].title;

              var updateArray = [];
              for (nodeId in scope.allEdges) {
                if (scope.allEdges.hasOwnProperty(nodeId)) {
                  updateArray.push(scope.allEdges[nodeId]);
                }
              }
              scope.edges.update(updateArray);
            } else {
              scope.allEdges[nodeId].label = '';
            }
          }
      };

        scope.blurEdge = function (params) {
            for (var nodeId in scope.allEdges) {
                scope.allEdges[nodeId].label = '';
            }
        };

        scope.afterDrawing = function (params) {
            if(!scope.info.doneRendering){
                scope.info.doneRendering = true;
                scope.network.setOptions({physics: {enabled: false}});
            }
        };
        scope.highlightGoGenes = function(goId){
            goGenes = scope.info.go_genes[goId];
            scope.info.highlightActive = true;

            for (var nodeId in scope.allNodes) {
                if(goGenes.indexOf(scope.allNodes[nodeId].label) > -1){
                    scope.allNodes[nodeId].color = "#00FF00";
                    scope.allNodes[nodeId].font.size = 40;
                } else {
                    scope.allNodes[nodeId].color = "rgba(150,150,150,0.75)";
                    scope.allNodes[nodeId].font.size = scope.allNodes[nodeId].permaFont.size;

                }

            }

            var updateArray = [];
            for (nodeId in scope.allNodes) {
              if (scope.allNodes.hasOwnProperty(nodeId)) {
                updateArray.push(scope.allNodes[nodeId]);
              }
            }
            scope.nodes.update(updateArray);
        };

        scope.neighborhoodHighlight = function(params) {
          // if something is selected:
          scope.info.annotationChecked = "NONE";
          if (params.nodes.length > 0) {
              var selectedNode = params.nodes[0];
              if(selectedNode === "tooltip1"){
                  scope.nodes.remove({id: "tooltip1"});
                  scope.$apply(function(){
                    scope.info.selectedNode = "";

                    scope.info.selectedClusterTitle = "Select Cluster";
                    scope.info.selectedClusterColor = "blank";
                    scope.info.selectedGeneTitle = "Select Gene";
                    scope.info.selectedAuthorTitle = "Select Author";
                  });

                  for (var nodeId in scope.allNodes) {
                    scope.allNodes[nodeId].color = scope.allNodes[nodeId].permaColor;
                    scope.allNodes[nodeId].font = scope.allNodes[nodeId].permaFont;
                    if (scope.allNodes[nodeId].hiddenLabel !== undefined) {
                      scope.allNodes[nodeId].label = scope.allNodes[nodeId].hiddenLabel;
                      scope.allNodes[nodeId].hiddenLabel = undefined;
                    }
                  }
                  scope.info.highlightActive = false
              } else {
                scope.info.highlightActive = true;

                for (var nodeId in scope.allNodes) {
                    if(scope.info.nodeValueType === "LOCALCC"){
                        scope.allNodes[nodeId].color = scope.allNodes[nodeId].clusterRGB;
                    } else {
                        scope.allNodes[nodeId].color = scope.allNodes[nodeId].expressionRGB;
                    }

                  if (scope.allNodes[nodeId].hiddenLabel !== undefined) {
                    scope.allNodes[nodeId].label = scope.allNodes[nodeId].hiddenLabel;
                    scope.allNodes[nodeId].hiddenLabel = undefined;
                  }
                }

                var updateArray = [];
                for (nodeId in scope.allNodes) {
                  if (scope.allNodes.hasOwnProperty(nodeId)) {
                    updateArray.push(scope.allNodes[nodeId]);
                  }
                }
                scope.nodes.update(updateArray);

                //================================
                // END - CLEAR PREVIOUS SELECTION
                //================================

                var i,j;
                //console.log(scope.allNodes[selectedNode].title);

                if (scope.$root.$$phase != '$apply' && scope.$root.$$phase != '$digest') {
                  scope.$apply(function(){
                    scope.info.selectedNode = scope.allNodes[selectedNode].label;
                  });
                }

                var degrees = 2;

                // mark all nodes as hard to read.
                for (var nodeId in scope.allNodes) {
                    scope.allNodes[nodeId].color = 'rgba(200,200,200,0.5)';
                    if (scope.allNodes[nodeId].hiddenLabel === undefined) {
                        scope.allNodes[nodeId].hiddenLabel = scope.allNodes[nodeId].label;
                        scope.allNodes[nodeId].label = undefined;
                    }
                }
                var connectedNodes = scope.network.getConnectedNodes(selectedNode);
                var allConnectedNodes = [];

                // get the second degree nodes
                for (i = 1; i < degrees; i++) {
                  for (j = 0; j < connectedNodes.length; j++) {
                    allConnectedNodes = allConnectedNodes.concat(scope.network.getConnectedNodes(connectedNodes[j]));
                  }
                }

                // all second degree nodes get a different color and their label back
                for (i = 0; i < allConnectedNodes.length; i++) {
                  scope.allNodes[allConnectedNodes[i]].color = 'rgba(150,150,150,0.75)';
                  if (scope.allNodes[allConnectedNodes[i]].hiddenLabel !== undefined) {
                    scope.allNodes[allConnectedNodes[i]].label = scope.allNodes[allConnectedNodes[i]].hiddenLabel;
                    scope.allNodes[allConnectedNodes[i]].hiddenLabel = undefined;
                  }
                }

                // all first degree nodes get their own color and their label back
                for (i = 0; i < connectedNodes.length; i++) {
                  scope.allNodes[connectedNodes[i]].color = undefined;
                  if (scope.allNodes[connectedNodes[i]].hiddenLabel !== undefined) {
                    scope.allNodes[connectedNodes[i]].label = scope.allNodes[connectedNodes[i]].hiddenLabel;

                    if(scope.info.nodeValueType === "LOCALCC"){
                        scope.allNodes[connectedNodes[i]].color = scope.allNodes[connectedNodes[i]].clusterRGB;
                    } else {
                        scope.allNodes[connectedNodes[i]].color = scope.allNodes[connectedNodes[i]].expressionRGB;
                    }

                    scope.allNodes[connectedNodes[i]].hiddenLabel = undefined;
                  }
                }

                // the main node gets its own color and its label back.
                scope.allNodes[selectedNode].color = scope.allNodes[selectedNode].permaColor;
                if (scope.allNodes[selectedNode].hiddenLabel !== undefined) {
                  scope.allNodes[selectedNode].label = scope.allNodes[selectedNode].hiddenLabel;
                  scope.allNodes[selectedNode].color = scope.allNodes[selectedNode].permaColor;
                  scope.allNodes[selectedNode].hiddenLabel = undefined;
                }
            }

          }
          else if (scope.info.highlightActive === true) {
              scope.nodes.remove({id: "tooltip1"});
            // reset all nodes

            for (var nodeId in scope.allNodes) {
                if(scope.info.nodeValueType === "LOCALCC"){
                    scope.allNodes[nodeId].color = scope.allNodes[nodeId].clusterRGB;
                } else {
                    scope.allNodes[nodeId].color = scope.allNodes[nodeId].expressionRGB;
                }
                scope.allNodes[nodeId].font = scope.allNodes[nodeId].permaFont;

              if (scope.allNodes[nodeId].hiddenLabel !== undefined) {
                scope.allNodes[nodeId].label = scope.allNodes[nodeId].hiddenLabel;
                scope.allNodes[nodeId].hiddenLabel = undefined;
              }
            }
            scope.info.highlightActive = false;

          // transform the object into an array
          var updateArray = [];
          for (nodeId in scope.allNodes) {
            if (scope.allNodes.hasOwnProperty(nodeId)) {
              updateArray.push(scope.allNodes[nodeId]);
            }
          }
          scope.nodes.update(updateArray);

          if (scope.$root.$$phase != '$apply' && scope.$root.$$phase != '$digest') {
              scope.$apply(function(){
              scope.info.selectedNode = "";

              scope.info.selectedClusterTitle = "Select Cluster";
              scope.info.selectedClusterColor = "blank";
              scope.info.selectedGeneTitle = "Select Gene";
              scope.info.selectedAuthorTitle = "Select Author";
            });
          }
        }

          if((scope.allNodes[selectedNode]) && (scope.allNodes[selectedNode].permaLabel)){
              scope.allNodes[selectedNode].permaLabel.title = "testing 1";
              //scope.allNodes[selectedNode].label = scope.allNodes[selectedNode].hiddenLabel;
              scope.allNodes[selectedNode].font.size = 40;
          }

          scope.nodes.remove({id: "tooltip1"});
          if(selectedNode != "tooltip1" && scope.allNodes[selectedNode]){
              urlstar = scope.pythonHost + "/api/gene/summary/" + scope.allNodes[selectedNode].permaLabel + "?callback=JSON_CALLBACK";

              var myrequestStar = HttpServiceJsonp.jsonp(urlstar)
              .success(function (result) {
                  var nodePosition = scope.network.getPositions(selectedNode);
                  console.log("x: " + nodePosition[selectedNode].x.toString() + " y: " + nodePosition[selectedNode].y.toString());

                  if(result.length > 60){
                      var newStr = "" + scope.allNodes[selectedNode].permaLabel + " \n\n" + result.replace(/(.{1,60})( +|$\n?)|(.{1,60})/g, "$1\n");
                      //var newStr = "" + scope.allNodes[selectedNode].permaLabel + " \n\n" + result.replace(/(.{1,60})( +|$\n?)|(.{1,60})/g, "$1\n");
                      scope.nodes.add({id: "tooltip1", label: newStr,
                      shape: "box", fixed: {x: true, y: true},
                      labelHighlightBold: false,
                      x: (nodePosition[selectedNode].x + 310), y: nodePosition[selectedNode].y,
                      borderWidth: 5,
                      borderWidthSelected: 1,
                      color: {background: "#F5F4ED", highlight: "#F5F4ED", border: "#F5F4ED"},
                      scaling: {label: {maxVisible: 40, drawThreshold: 5}},
                      font: {background: "#F5F4ED", size: 20, align: 'left'}
                      });
                  } else if(result.length > 0) {
                      splitLength = result.length / 2;
                      var newStr = "" + scope.allNodes[selectedNode].permaLabel + " \n\n" + result.replace(/(.{1,splitLength})( +|$\n?)|(.{1,splitLength})/g, "$1\n");
                      //var newStr = "LOC729082,KCNQ5,IKZF4,LRFN4,GABBR1,FAM55C,ZNF710,OR5L1,SMTNL2,C15orf40,MEGF6,GFI1B,ZNF787,HOMER3,RCAN3,LHFP,DKK3,ZFPM1,LOC728743,LCA5,RPTOR,EPHB1,NUDCD3,GNG13,HOXB7\n,NRXN1,FIGN,ZNF468,SRRM3,FASTKD2,TAGAP,ENPP5,SPTBN4,SPTBN5,C8orf85,DSCAML1,PTPRE,COTL1,WNT4,C20orf43,HIST1H2AJ,COX7A2,CADPS2,TSHZ3,LOC400027,CHRNA4,NEU1,PDZK1,CCDC19,C6orf221,DNAJB6,PTPRS,MTMR15,SEMA3G,DCLK2,ZNF777,ADARB2,KRTAP25-1,HS2ST1,TPO,SNED1,PARD3B,CDYL2,FOXH1,SYNGAP1,AATK,MIR612,GNPTAB,PPIB,WSCD1,C1orf212,JAM3,TOX2,TALDO1,RASSF1,NLK,MPV17L2,REPS2,ZNF786,GPD1L,MRPL35,TMUB1,CTBP1,SLC46A3,CLK2P,TFCP2,MLH3,ERICH1,NEU1,KCNMA1,PRAM1,MYNN,ELMO3,NXN,PER2,WWOX,GRB7,CDK17,RALYL,GON4L,TCEB3,PSD,LTV1,MAD1L1,CLINT1,EIF4G2,CAPN10,NFKBIL2,ANKRD11,DNAH12,MPZL3,BAHCC1,PTPRO,LMO7,RIMBP2,SLC43A1,RNF160,C20orf196,ZBTB9,MYH10,HES1,NMUR1,ZMIZ1,AZI2,CCDC42,FAM19A5,BIRC3,FAM83H,GPC6,CENPF,FBN3,ARRDC2,VSX1,STT3A,PKHD1,STK32C,TRIM45,FOXS1,PAX7,KCNQ2,USP40,KIAA1370,GPR56,RETSAT,SYT11,AKR7A3,PLEKHA6,APOF,CASC4,NT5C,NDUFS8,PLA2R1,RPSA,C22orf30,CXorf15,FAM19A5,CCR8,SLC16A9,APBA1,COL6A6,EPPK1";
                      scope.nodes.add({id: "tooltip1", label: newStr, shape: "box", labelHighlightBold: false,
                      x: (nodePosition[selectedNode].x + 60 + ((result.length + 20) * 3)), y: nodePosition[selectedNode].y,
                      color: {background: "#F5F4ED", border: "#c0c0c0"},
                      scaling: {label: {maxVisible: 40, drawThreshold: 5}},
                      font: {background: "#F5F4ED", size: 20}});
                  } else {
                      scope.nodes.add({id: "tooltip1", label: "Summary n/a", shape: "box", labelHighlightBold: false,
                      x: (nodePosition[selectedNode].x + 99), y: nodePosition[selectedNode].y,
                      color: {background: "#F5F4ED", border: "#c0c0c0"},
                      scaling: {label: {maxVisible: 40, drawThreshold: 5}},
                      font: {background: "#F5F4ED", size: 20}});
                  }

                  scope.allNodes[selectedNode].permaLabel.title = result;
                  var updateArray = [];
                  for (nodeId in scope.allNodes) {
                    if (scope.allNodes.hasOwnProperty(nodeId)) {
                      updateArray.push(scope.allNodes[nodeId]);
                    }
                  }
                  scope.nodes.update(updateArray);
              }).finally(function () {
              }).error(function (data, status, headers, config) {
                  alert(data + ' - ' + status + ' - ' + headers);
              });
          }
        }
    }

    return {
      scope: {
          result: "=",
          clusterId: "=",
          overlapGeneList: "=",
          verticalHeight: "=",
          clusterTitle: "=",
          isSimpleDisplay: "=",
          heatOverlapNodes: "=",
          heatDrugGenes: "=",
          nodeFilterCount: "@"
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/VisJS_heatmap_directive.html",
      link: link
    };
});

app.directive('continuousLegendSlider', function (HttpServiceJsonp, $timeout) {
    function link(scope, el, attrs) {
        scope.rangeSlider = {
            val: 0
        };

        scope.uniqueId = 'legendVis' + uniqueId++;

        scope.info = {
            permaMaxVal: 0.0,
            permaMinVal: 0.0,
            leftColor: '',
            rightColor: '',
        };
        //scope.slider.minValue = 0.0;
        //scope.slider.maxValue = 1.0;
        var scale = chroma.scale([scope.leftColor, scope.rightColor]);//.colors(10);

        scope.info.leftColor = scale(0.0).hex();
        scope.info.rightColor = scale(1.0).hex();

        scope.info.permaMinVal = scope.rangeMin;
        scope.info.permaMaxVal = scope.rangeMax;

        scope.updateMax = function(){
            if(scope.rangeMax){
                if(scope.rangeMax <= scope.info.permaMaxVal){
                    if(scope.rangeMax < scope.rangeMin){
                        scope.rangeMax = scope.rangeMin;
                    }
                    var scaleVal = (scope.rangeMax)/(scope.info.permaMaxVal - scope.info.permaMinVal)

                    scope.info.rightColor = scale(scaleVal).hex();
                    console.log("scale value: " + scaleVal);
                } else {
                    scope.rangeMax = scope.info.permaMaxVal;
                }
            }
        }

        scope.updateMin = function(){
            if(scope.rangeMin){
                if(scope.rangeMin >= scope.info.permaMinVal){
                    if(scope.rangeMin > scope.rangeMax){
                        scope.rangeMin = scope.rangeMax;
                    }
                    var scaleVal = (scope.rangeMin)/(scope.info.permaMaxVal - scope.info.permaMinVal)

                    scope.info.leftColor = scale(scaleVal).hex();
                    console.log("scale value: " + scaleVal);
                } else {
                    scope.rangeMin = scope.info.permaMinVal;
                }
            }
        }

    }
    var uniqueId = 1;
    return {
      scope: {
          result: "=",
          leftColor: "@",
          rightColor: "@",
          middleColor: "@",
          dirId: "=",
          rangeOutput: "=",
          rangeMin: "@",
          rangeMax: "@",
          rangeStep: "@",
          rangeTitle: "@",
          reOrderLayout: "&"
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/continuous_slider_directive.html",
//      template:
//            "<style>input[type=range]#{{::uniqueId}}::-webkit-slider-runnable-track {width: 300px; height: 25px; background-image: "
//            + "linear-gradient(to right,{{leftColor}},{{rightColor}}); border: none; border-radius: 6px;}</style>"
//            + "<input type='range' value=0 id='{{::uniqueId}}' ng-model='rangeOutput' min='0' max='1' step='0.01' "
//            + "style='width:200px; margin-top: 20px; margin-left: 20px; margin-right: 10px; display: inline;'>",
      link: link
    };
});



/*
==========================================
==========================================
        LEGEND SHAPE DESCRIPTION
        DIRECTIVE
==========================================
==========================================
*/
app.directive('legendDescriptions', function () {
    function link(scope, el, attrs) {
        scope.info = {
            "shapesArray": [
                {title: "Gene", shapeType: "icon", shapeSource: "circle-icon"},
                {title: "miRNA", shapeType: "icon", shapeSource: "triangle-icon"},
                {title: "DNA Mutation", shapeType: "image", shapeSource: "../images/diamond.png"},
                {title: "Query Gene", shapeType: "image", shapeSource: "../images/query_gene.png"}
            ]
        }
    }

    return {
      scope: {
          shapes: "="
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/legend_shape_descriptions_directive.html",
      link: link
    };
});

/*
==========================================
==========================================
        SIMPLE CIRCLE SHAPE FOR
        ANNOTATIONS DIRECTIVE
==========================================
==========================================
*/
app.directive('annotationsCircle', function () {
    function link(scope, el, attrs) {
        scope.info = {
            "itemId": ""
        }

        scope.$watch('info.itemId', function() {
            scope.hoveredItemId = scope.info.itemId;
        });

        scope.callControllerFunc = function(GO_id) {
            scope.annotationChecked = GO_id;
            scope.getGenesFromGoid({goid: GO_id});
        }

    }

    return {
      scope: {
          annotations: "=",
          hoveredItemId: "=",
          getGenesFromGoid: "&",
          annotationChecked: "="
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/annotations_circle_directive.html",
      link: link
    };
});

/*
==========================================
==========================================
        ENRICHMENT
        DIRECTIVE
==========================================
==========================================
*/
app.directive('clusterEnrichment', function (HttpServiceJsonp, $timeout) {
    function link(scope, el, attrs) {
        scope.pythonHost = python_host_global;
        var esId = scope.clusterId;
        var url = scope.pythonHost + "/api/elasticsearch/getclusterenrichmentbyid/" + esId + "?callback=JSON_CALLBACK";
        var myrequest = HttpServiceJsonp.jsonp(url)
             .success(function (result) {
                  scope.modalData = result;
             }).finally(function () {
        }).error(function (data, status, headers, config) {
            alert(data + ' - ' + status + ' - ' + headers);
        });
    }

    return {
      scope: {
          result: "=",
          clusterId: "="
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/enrichmentByEsId_directive.html",
      link: link
    };
});

/*
==========================================
==========================================
        HEATMAP MATRIX
        DIRECTIVE
==========================================
==========================================
*/
app.directive('heatMapMatrix', function (HttpServiceJsonp, $timeout) {
    function link(scope, el, attrs) {

    scope.$on('$destroy', function() {
        console.log("destroy");
        $('#heatmap').html('');
    });

        scope.pythonHost = python_host_global;
        console.log("REST services endpoint (Plotly_heatmapApp): " + scope.pythonHost);
      //scope.pythonHost = "http://localhost:8182"; // Localhost
          //scope.pythonHost = "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com"; // PROD
      //scope.pythonHost = "http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com"; //Search Engine (Dev)
      //scope.pythonHost = "http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:8181"; //Search Engine (Prod)

      scope.esId = "";
      scope.title = "";
      scope.plotlyData = {
        "passThisDataAlong": {},
        "passThisLayoutAlong": {},
        "xValues": [],
        "yValues": [],
        "zValues": [],
        "exportRowTarget": "",
        "exportColumnTarget": "",
        "exportArray": [],
        "heatmapFullHeight": 1000,
        "heatmapFullWidth": 1000,
        "heatmapScaledHeight": 530,
        "heatmapScaledWidth": 530,
        "isFullSize": false,
        "isNewWindow": false
      }

          $('#heatmapIsLoading').html('<span class="fa fa-spinner fa-2x fa-pulse"></span>');
          var myPlot = document.getElementById('heatmap')
          var heatmap_title = "";
          scope.esId = scope.clusterId;
          scope.title = "Change this title";
          scope.plotlyData.isFullSize = false;//scope.GetQueryStringParams("showFullSize");
          if(typeof scope.plotlyData.isFullSize === 'undefined'){
            scope.plotlyData.isFullSize = false;
          } else {
            scope.plotlyData.isNewWindow = true;
          }

          //var url = scope.pythonHost + "/nav/elasticsearch/getheatmap3/" + scope.esId + "?callback=JSON_CALLBACK";
          var url = scope.pythonHost + "/api/getheatmapmatrix/filtered/" + scope.esId + "/" + scope.overlapGeneList + "/" + scope.nodeFilterCount + "?callback=JSON_CALLBACK";

          console.log(url);
          $('#heatmap').css( "display", "none" );
          var myrequest = HttpServiceJsonp.jsonp(url)
               .success(function (result) {
                 //$('#heatmapIsLoading').html('<h4>Cluster - ' + scope.title + '</h4>');
                 $('#heatmapIsLoading').html('');

                 //===========================================
                 // calculate the full size height and width
                 //===========================================
                 scope.plotlyData.heatmapFullHeight = 22 * result.yValues.length + 180;
                 scope.plotlyData.heatmapFullWidth = 22 * result.xValues.length + 100;

                 if(scope.plotlyData.isFullSize){
                   height = scope.plotlyData.heatmapFullHeight;
                   width = scope.plotlyData.heatmapFullWidth;
                 } else {
                   height = scope.plotlyData.heatmapScaledHeight;
                   width = scope.plotlyData.heatmapScaledWidth;
                 }

                 $('#heatmap').width(width).height(height);

                 scope.plotlyData.xValues = result.xValues;
                 scope.plotlyData.yValues = result.yValues;

                 for(var i=0; i<scope.plotlyData.xValues.length; i++){
                     scope.plotlyData.xValues[i] = scope.plotlyData.xValues[i].replace("_g","").replace("_v","").replace("_m","");
                 }

                 for(var i=0; i<scope.plotlyData.yValues.length; i++){
                     scope.plotlyData.yValues[i] = scope.plotlyData.yValues[i].replace("_g","").replace("_v","").replace("_m","");
                 }

                 scope.plotlyData.zValues = result.zValues;

                 var colorscaleValue = [
                   [0, '#ee4035'],
                   [1, '#0392cf']
                 ];

                 var data = [{
                   x: scope.plotlyData.xValues,
                   y: scope.plotlyData.yValues,
                   z: scope.plotlyData.zValues,
                   type: 'heatmap',
                   autocolorscale: false,
                   //zsmooth: 'fast',
                   colorscale: 'Picnic',
                   zmax: 1.0,
                   zmin: -1.0
                 }];

                 var layout = {
                   title: '',
                   annotations: [],
                   xaxis: {
                     ticks: '',
                     side: 'top',
                     width: 700,
                     height: 700,
                     autosize: true
                   },
                   yaxis: {
                     ticks: '',
                     ticksuffix: ' ',
                     width: 700,
                     height: 700,
                     autosize: true
                   }
                 };

                 scope.plotlyData.passThisDataAlong = data;
                 scope.passThisLayoutAlong = layout;

                 Plotly.newPlot('heatmap', data, layout, {showLink: false});
                 //Plotly.addTraces('heatmap', {y: [1, 5, 7]}, 0);

      /*
                 $('#heatmap').on('plotly_click', function(myData){
                   var plotDiv = document.getElementById('heatmap');
                    console.log(plotDiv.data);
                    console.log(myData.target._hoverdata[0].y);

                    if (scope.$root.$$phase != '$apply' && scope.$root.$$phase != '$digest') {
                      scope.$apply(function(){
                        scope.plotlyData.exportRowTarget = myData.target._hoverdata[0].y;
                        scope.plotlyData.exportColumnTarget = myData.target._hoverdata[0].x;
                      });
                    }

                    //alert(myData.target._hoverdata[0].y);
                    //alert('Closest point clicked: ');
                });
      */
                 $('#heatmap').css( "display", "block" );
               }).finally(function () {
          }).error(function (data, status, headers, config) {
                        alert(data + ' - ' + status + ' - ' + headers);
          });

      scope.GetQueryStringParams = function(sParam)
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

      scope.openPlotlyExternal = function(){
          var hiddenForm = $('<div id="hiddenform" '+
              'style="display:none;">'+
              '<form action="https://plot.ly/external" '+
              'method="post" target="_blank">'+
              '<input type="text" '+
              'name="data" /></form></div>')
              .appendTo('body');
          var graphData = JSON.stringify(scope.getPlotlyGraph());
          hiddenForm.find('input').val(graphData);
          hiddenForm.find('form').submit();
          hiddenForm.remove();
          return false;
      };

      scope.openInNewWindow = function() {
        $window.open(window.location.href);//"http://geneli.st:8181/Prototype2/partials/Plotly_heatmap.html?geneList=OR2J3&termId=my%20title&clusterId=" + scope.esId + "&networkTitle=my%20title&showFullSize=true");
      }

      scope.resizeHeatMap = function() {
        //======================================
        // Flip the size toggle and take action
        //======================================
        scope.plotlyData.isFullSize = !scope.plotlyData.isFullSize;

        if(scope.plotlyData.isFullSize){
          var heatMapDiv = $('#heatmap').width(scope.plotlyData.heatmapFullWidth).height(scope.plotlyData.heatmapFullHeight);

          var update = {
            width: scope.plotlyData.heatmapFullWidth,
            height: scope.plotlyData.heatmapFullHeight
          };

          Plotly.relayout('heatmap', update);
        } else { // Scaled size
          var heatMapDiv = $('#heatmap').width(scope.plotlyData.heatmapScaledWidth).height(scope.plotlyData.heatmapScaledHeight);

          var update = {
            width: scope.plotlyData.heatmapScaledWidth,
            height: scope.plotlyData.heatmapScaledHeight
          };

          Plotly.relayout('heatmap', update);
        }
      }

      scope.getPlotlyGraph = function(){
          return {
              data: scope.plotlyData.passThisDataAlong,
              layout: scope.passThisLayoutAlong
          };
      };

      scope.exportData = function(){
        console.log("x: " + scope.plotlyData.xValues.length + " y: " + scope.plotlyData.yValues.length + " z: " + scope.plotlyData.zValues[0].length);
        scope.plotlyData.exportArray = Array(scope.plotlyData.yValues.length + 1);
        //=========================
        // Print the table header
        //=========================
        var tempHeader = ",";
        for (var i = 0; i < scope.plotlyData.xValues.length; i++) {
          tempHeader += scope.plotlyData.xValues[(scope.plotlyData.xValues.length - 1) - i] + ",";
        }
        //scope.plotlyData.exportArray[0] = tempHeader;
        scope.plotlyData.exportArray[0] = scope.getXLabels();

        for (var i = 0; i < scope.plotlyData.yValues.length; i++)
        {
          //==============================================
          // The first value in the row is the row label
          //==============================================
          var tempRowString = scope.plotlyData.yValues[i] + ",";
          for (var j = 0; j < scope.plotlyData.xValues.length; j++)
          {
            tempRowString += scope.plotlyData.zValues[i][j] + ",";
          }
          scope.plotlyData.exportArray[(scope.plotlyData.yValues.length) - i] = tempRowString;
        }

        var exportArrayString = "data:text/csv;charset=utf-8,";
        for (var k = 0; k <= scope.plotlyData.yValues.length; k++) {
            exportArrayString += scope.plotlyData.exportArray[k] + '\n';
        }
        console.log(exportArrayString);
        var encodedUri = encodeURI(exportArrayString);
        window.open(encodedUri);
        //console.log(scope.plotlyData.exportArray);

        //$('#heatmap').html('<div class="panel panel-default"><div class="panel-body">' + scope.plotlyData.zValues + '</div></div>');

      };

      scope.exportXData = function(){
        var exportArrayString = "data:text/csv;charset=utf-8,";
        for (var i = 0; i < scope.plotlyData.xValues.length; i++) {
            exportArrayString += scope.plotlyData.xValues[i] + '\n';
        }

        var encodedUri = encodeURI(exportArrayString);
        window.open(encodedUri);
      };

      scope.exportYData = function(){
        var exportArrayString = "data:text/csv;charset=utf-8,";
        for (var i = 0; i < scope.plotlyData.yValues.length; i++) {
            exportArrayString += scope.plotlyData.yValues[i] + '\n';
        }

        var encodedUri = encodeURI(exportArrayString);
        window.open(encodedUri);
      };

      scope.getXLabels = function(){
        var tempHeader = ",";
        for (var i = 0; i < scope.plotlyData.xValues.length; i++) {
          tempHeader += scope.plotlyData.xValues[i] + ",";
        }

        return tempHeader;
      };

      scope.getYLabels = function(){
        var tempHeader = ",";
        for (var i = 0; i < scope.plotlyData.yValues.length; i++) {
          tempHeader += scope.plotlyData.yValues[(scope.plotlyData.yValues.length - 1) - i] + ",";
        }

        return tempHeader;
      };
    }

    return {
      scope: {
          result: "=",
          clusterId: "=",
          overlapGeneList: "=",
          nodeFilterCount: "@"
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/Plotly_heatmap_directive.html",
      link: link
    };
});

app.directive( 'editInPlace', function($log) {
    return {
        restrict: 'AE',
        scope: {
            value: '=',
            onBlur: '&',
            placeholder: '@',
            default: '@'
        },
        template: '<a style="cursor: pointer; text" ng-click="edit()">{{display()}}</a><input type="text" style="width: 35px; margin-top: -12px; padding-left: 3px; padding-right: 3px;" class="form-control inline input-sm" ng-model="value" ng-blur="blur()" placeholder="{{placeholder}}" ng-keyup="$event.keyCode == 13 ? blur() : null" style="width: auto; height: 2em"/>',
        link: function ( $scope, element, attrs ) {

            // give the element a class so we can style it
            element.addClass( 'edit-in-place' );

            // get a reference to the input element
            var inputElement = element.find('input');

            // ng-click handler to activate edit-in-place
            $scope.edit = function () {
                // take a snapshot of the clean value before editing
                $scope.clean = $scope.value;

                // allow us to style the element using css
                element.addClass( 'active' );

                // focus on the input element
                inputElement[0].focus();
            };

            // display placeholder if value is not valid
            $scope.display = function () {
                return !$scope.value ? $scope.default || $scope.placeholder || "Undefined" : $scope.value;
            }

            // blur handler removes active state and calls user onBlur callback
            $scope.blur = function() {
                element.removeClass('active');
                if ($scope.clean != $scope.value) {
                    $scope.onBlur();
                }
            };
        }
    };
});

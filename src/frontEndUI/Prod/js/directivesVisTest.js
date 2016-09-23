var app = angular.module('testApp');

app.directive('annotationsCircle', function () {
    function link(scope, el, attrs) {
        scope.info = {
            "itemId": "",
            "annotationChecked": "NONE"
        }

        scope.$watch('info.itemId', function() {
            scope.hoveredItemId = scope.info.itemId;
        });

        scope.callControllerFunc = function(GO_id) {
            scope.getGenesFromGoid({goid: GO_id});
        }

    }

    return {
      scope: {
          annotations: "=",
          hoveredItemId: "=",
          getGenesFromGoid: "&"
      },
      restrict: "EA",
      templateUrl: "directiveTemplates/annotations_circle_directive.html",
      link: link
    };
});
/*
==========================================
==========================================
        ABCDEF
        DIRECTIVE
==========================================
==========================================
*/
app.directive('visDisplay', function ($http, $timeout) {
    function link(scope, el, attrs) {
        scope.uniqueId = 'visDiv' + uniqueId++;

        var esId = scope.clusterId;
        var url = "http://ec2-52-32-210-84.us-west-2.compute.amazonaws.com:8182/ds/getheatmapgraph/" + esId + "/NOGENELIST?callback=JSON_CALLBACK";
        $http.jsonp(url)
		.then(function (response) {
             var results = response.data;

 		   var nodeArray = [];
 		   var edgeArray = [];

 		   for(var i=0; i<results.nodes.length; i++){
 			   nodeArray.push({id: i, label: results.nodes[i].id, font: {size: 20},
 			   color: {background: '#CC0000', border: '#c0c0c0'}, shape: 'dot', size: 20}
 			   );
 		   }

 		   for(var i=0; i<results.links.length; i++){
 			 edgeArray.push({from: results.links[i].source, to: results.links[i].target,
 			 	font: {align: 'horizontal', size: 20, background: 'rgba(255,255,255,255)'},
 				title: results.links[i].weight,color: { color: '#00CC00'}}
 			 );
 		   }

 			scope.nodes = new vis.DataSet(nodeArray);
 			scope.edges = new vis.DataSet(edgeArray);

 			var container = document.getElementById('visDiv');
 			var data = {
 			  edges: scope.edges,
 			  nodes: scope.nodes
 			};
 			var options = {
                autoResize: true,
                height: '100%',
                width: '100%',
                nodes: {
                 scaling: {
                   min: 10,
                   max: 30,
                   label: {
                     min: 8,
                     max: 30,
                     drawThreshold: 12,
                     maxVisible: 20
                   }
                 }
                },
                interaction:{
                  hover:true,
                  zoomView: true
                },
                physics: {
                 enabled: false
                }
               };

 			scope.network = new vis.Network(container, data, options);
        });
    }
    var uniqueId = 1;
    return {
      scope: {
          result: "=",
          clusterId: "="
      },
      restrict: "EA",
      templateUrl: "directiveTemplates/vis_directive.html",
      link: link
    };
});

app.directive('continuousLegendSlider', function (HttpServiceJsonp, $timeout) {
    function link(scope, el, attrs) {
        scope.rangeSlider = {
            val: 0
        };
        scope.info = {
            permaMaxVal: 0.0,
            permaMinVal: 0.0,
            leftColor: '',
            rightColor: '',
        };
        //scope.slider.minValue = 0.0;
        //scope.slider.maxValue = 1.0;
        var scale = null;
        if(scope.middleColor != null){
            scale = chroma.scale([scope.leftColor, scope.middleColor, scope.rightColor]);//.colors(10);
        } else {
            scale = chroma.scale([scope.leftColor, scope.rightColor]);//.colors(10);
        }

        scope.info.leftColor = scale(0.0).hex();
        scope.info.rightColor = scale(1.0).hex();

        scope.info.permaMinVal = scope.rangeMin;
        scope.info.permaMaxVal = scope.rangeMax;
        //scope.leftColor = scale(0.7).hex();
        //console.log(scope.leftColor);
        //console.log("Done");
        //scope.rightColor = "#00FF00";

/*
        scope.$watch('rangeMin', function() {
            if(scope.rangeMin){
                if(scope.rangeMin >= scope.info.permaMinVal){
                    if(scope.rangeMin > scope.rangeMax){
                        scope.rangeMin = scope.rangeMax;
                    }
                    var scaleVal = (scope.rangeMin)/(scope.info.permaMaxVal - scope.info.permaMinVal)

                    scope.info.leftColor = scale(scaleVal).hex();
                    console.log("scale value: " + scaleVal);
                }
                //console.log('rangeMin: ' + scope.rangeMin);
            }
        });

        scope.$watch('rangeMax', function() {
            if(scope.rangeMax){
                if(scope.rangeMax <= scope.info.permaMaxVal){
                    if(scope.rangeMax < scope.rangeMin){
                        scope.rangeMax = scope.rangeMin;
                    }
                    var scaleVal = (scope.rangeMax)/(scope.info.permaMaxVal - scope.info.permaMinVal)

                    scope.info.rightColor = scale(scaleVal).hex();
                    console.log("scale value: " + scaleVal);
                }
                //console.log('rangeMin: ' + scope.rangeMin);
            }
        });
*/

        //=============================
        //=============================
        //=============================
        // LEGEND
        // GROUP GENES BY CLUSTER
        //=============================
        //=============================
        //=============================

        scope.uniqueId = 'legendVis' + uniqueId++;

        scope.updateMax = function(){
            if(scope.rangeMax){
                if(scope.rangeMax <= scope.info.permaMaxVal){
                    if(scope.rangeMax < scope.rangeMin){
                        scope.rangeMax = scope.rangeMin;
                    }
                    var scaleVal = (scope.rangeMax)/(scope.info.permaMaxVal - scope.info.permaMinVal)

                    scope.info.rightColor = scale(scaleVal).hex();
                    console.log("scale value: " + scaleVal);
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
                }
                //console.log('rangeMin: ' + scope.rangeMin);
            }
        }

        scope.init_page = function(){
            var geneClust = {};
            var queryGeneClust = {};
            var legendNodeArray = [];

            //==================
            // NODES Legend
            //==================
             legendNodeArray.push({id: "left_arrow", label: '', image: "../../images/slider4.png", shadow: {enabled: false}, size: 9, fixed: {x: false, y: true}, shape: 'image', x: 5, y: 0});
             //legendNodeArray.push({id: "leg_header1", label: "Nodes", title: "", font: {size: 20}, color: {'background':'#3F8CCC', 'border': '#3F8CCC'}, shadow: false, shape: 'text', permaSize: 20, x: 10, y: -5, fixed: true});
             //legendNodeArray.push({id: "leg_header1box", label: "0.00", title: "", font: {color: '#FDFDFD', size: 20}, color: {'background':'#3F8CCC', 'border': '#3F8CCC'}, shadow: false, shape: 'box', permaSize: 20, x: 10, y: 25, fixed: true});
             legendNodeArray.push({id: "legx_xyz1", label: "", title: "", borderWidth: 0, color: {'background':scope.leftColor, 'border': scope.leftColor}, size: 0, font: {size: 1}, shape: 'dot', permaColor: '#00FFFF', permaSize: 1, x: 0, y: 0, fixed: true});
             legendNodeArray.push({id: "legx_xyz2", label: "", title: "", borderWidth: 0, color: {'background':scope.rightColor, 'border': scope.rightColor}, size: 0, font: {size: 1}, shape: 'dot', permaColor: '#FF00FF', permaSize: 1, x: 200, y: 0, fixed: true});
             //legendNodeArray.push({id: "leg_text_xyz1", label: "0.0", title: "", font: {size: 20}, shadow: false, shape: 'text', permaSize: 20, x: 0, y: 0, fixed: true});
             //legendNodeArray.push({id: "leg_text_xyz2", label: "1.0", title: "", font: {size: 20}, shadow: false, shape: 'text', permaSize: 20, x: 200, y: 0, fixed: true});

            var legendEdgeArray = [
                {
                     from: "legx_xyz1",
                     to: "legx_xyz2",
                     label: "",
                     color: {
                         inherit: "both"
                     },
                     width: 20,
                     hoverWidth: 0
                 }
            ];

            scope.legendNodeArray = new vis.DataSet(legendNodeArray);
            scope.allLegendNodes = scope.legendNodeArray.get({returnType:"Object"});
            console.log(scope.uniqueId);
            //var legendContainer = el.find(scope.uniqueId);
            var legendContainer = document.getElementById(scope.uniqueId);
            console.log(legendContainer);
            //$('#legendVis').css('height', 60 );

            var legenedData = {
              nodes: scope.legendNodeArray,
              edges: legendEdgeArray
            };

            var legendOptions = {
               autoResize: false,
               height: '200px',
               width: '35px',
               nodes: {
                borderWidth: 1,
                shape: 'dot',
                shadow:true,
                font: {
                  size: 12,
                  face: 'Tahoma'
                },
                size: 16
               },
               clickToUse: true,
               interaction:{
                 hover: true,
                 dragView: false,
                 zoomView: false
               },
               physics: {
                enabled: false
               }
              };

           scope.legendNetwork = new vis.Network(legendContainer, legenedData, legendOptions);
           scope.legendNetwork.fit();
           console.log("scale: ");
           console.log(scope.legendNetwork.getScale());
        }
        $timeout(function() {
            //scope.init_page();

       }, 200);

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
          rangeTitle: "@"
      },
      restrict: "EA",
      templateUrl: "../partials/directiveTemplates/continuous_slider_directive.html",
//      template:
            //"Hi<div id='{{::uniqueId}}' style='width: 200px; height: 35px; border: 2px solid black;' class='gradientx'></div><input type='range' style='width:200px;'>",
//            "<style>input[type=range]#{{::uniqueId}}::-webkit-slider-runnable-track {width: 300px; height: 25px; background-image: "
//            + "linear-gradient(to right,{{leftColor}},{{rightColor}}); border: none; border-radius: 6px;}</style>"
//            + "<div style='font-size: 16px; font-weight: bold; margin-bottom: 5px; margin-left: 10px;'>{{rangeTitle}}</div>"
//            + "<input type='range' value=0 id='{{::uniqueId}}' ng-model='rangeOutput' style='width:200px;'>",
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

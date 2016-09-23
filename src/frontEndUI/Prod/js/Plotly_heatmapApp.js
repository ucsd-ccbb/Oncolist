
var app = angular.module('heatmapApp', ['services']);

// Code borrowed from stackoverflow user Anthony O. - May 15th 2014
app.config(['$httpProvider', function($httpProvider) {
    if (!$httpProvider.defaults.headers.get) {
        $httpProvider.defaults.headers.get = {};
    }
    $httpProvider.defaults.headers.get['If-Modified-Since'] = 'Mon, 26 Jul 1997 05:00:00 GMT';
    $httpProvider.defaults.headers.get['Cache-Control'] = 'no-cache';
    $httpProvider.defaults.headers.get['Pragma'] = 'no-cache';
}]);

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

app.controller('heatmapCtrl', function ($scope, $http, $log, $filter, HttpServiceJsonp, $location, $timeout, $window) {
    $scope.pythonHost = python_host_global;
    console.log("REST services endpoint (Plotly_heatmapApp): " + $scope.pythonHost);
  //$scope.pythonHost = "http://localhost:8182"; // Localhost
      //$scope.pythonHost = "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com"; // PROD
  //$scope.pythonHost = "http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com"; //Search Engine (Dev)
  //$scope.pythonHost = "http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:8181"; //Search Engine (Prod)

  $scope.esId = "";
  $scope.title = "";
  $scope.plotlyData = {
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

  $scope.GetQueryStringParams = function(sParam)
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

  $scope.openPlotlyExternal = function(){
      var hiddenForm = $('<div id="hiddenform" '+
          'style="display:none;">'+
          '<form action="https://plot.ly/external" '+
          'method="post" target="_blank">'+
          '<input type="text" '+
          'name="data" /></form></div>')
          .appendTo('body');
      var graphData = JSON.stringify($scope.getPlotlyGraph());
      hiddenForm.find('input').val(graphData);
      hiddenForm.find('form').submit();
      hiddenForm.remove();
      return false;
  };

  $scope.openInNewWindow = function() {
    $window.open(window.location.href);//"http://geneli.st:8181/Prototype2/partials/Plotly_heatmap.html?geneList=OR2J3&termId=my%20title&clusterId=" + $scope.esId + "&networkTitle=my%20title&showFullSize=true");
  }

  $scope.resizeHeatMap = function() {
    //======================================
    // Flip the size toggle and take action
    //======================================
    $scope.plotlyData.isFullSize = !$scope.plotlyData.isFullSize;

    if($scope.plotlyData.isFullSize){
      var heatMapDiv = $('#heatmap').width($scope.plotlyData.heatmapFullWidth).height($scope.plotlyData.heatmapFullHeight);

      var update = {
        width: $scope.plotlyData.heatmapFullWidth,
        height: $scope.plotlyData.heatmapFullHeight
      };

      Plotly.relayout('heatmap', update);
    } else { // Scaled size
      var heatMapDiv = $('#heatmap').width($scope.plotlyData.heatmapScaledWidth).height($scope.plotlyData.heatmapScaledHeight);

      var update = {
        width: $scope.plotlyData.heatmapScaledWidth,
        height: $scope.plotlyData.heatmapScaledHeight
      };

      Plotly.relayout('heatmap', update);
    }
  }

  $scope.getPlotlyGraph = function(){
      return {
          data: $scope.plotlyData.passThisDataAlong,
          layout: $scope.passThisLayoutAlong
      };
  };

  $scope.exportData = function(){
    console.log("x: " + $scope.plotlyData.xValues.length + " y: " + $scope.plotlyData.yValues.length + " z: " + $scope.plotlyData.zValues[0].length);
    $scope.plotlyData.exportArray = Array($scope.plotlyData.yValues.length + 1);
    //=========================
    // Print the table header
    //=========================
    var tempHeader = ",";
    for (var i = 0; i < $scope.plotlyData.xValues.length; i++) {
      tempHeader += $scope.plotlyData.xValues[($scope.plotlyData.xValues.length - 1) - i] + ",";
    }
    //$scope.plotlyData.exportArray[0] = tempHeader;
    $scope.plotlyData.exportArray[0] = $scope.getXLabels();

    for (var i = 0; i < $scope.plotlyData.yValues.length; i++)
    {
      //==============================================
      // The first value in the row is the row label
      //==============================================
      var tempRowString = $scope.plotlyData.yValues[i] + ",";
      for (var j = 0; j < $scope.plotlyData.xValues.length; j++)
      {
        tempRowString += $scope.plotlyData.zValues[i][j] + ",";
      }
      $scope.plotlyData.exportArray[($scope.plotlyData.yValues.length) - i] = tempRowString;
    }

    var exportArrayString = "data:text/csv;charset=utf-8,";
    for (var k = 0; k <= $scope.plotlyData.yValues.length; k++) {
        exportArrayString += $scope.plotlyData.exportArray[k] + '\n';
    }
    console.log(exportArrayString);
    var encodedUri = encodeURI(exportArrayString);
    window.open(encodedUri);
    //console.log($scope.plotlyData.exportArray);

    //$('#heatmap').html('<div class="panel panel-default"><div class="panel-body">' + $scope.plotlyData.zValues + '</div></div>');

  };

  $scope.exportXData = function(){
    var exportArrayString = "data:text/csv;charset=utf-8,";
    for (var i = 0; i < $scope.plotlyData.xValues.length; i++) {
        exportArrayString += $scope.plotlyData.xValues[i] + '\n';
    }

    var encodedUri = encodeURI(exportArrayString);
    window.open(encodedUri);
  };

  $scope.exportYData = function(){
    var exportArrayString = "data:text/csv;charset=utf-8,";
    for (var i = 0; i < $scope.plotlyData.yValues.length; i++) {
        exportArrayString += $scope.plotlyData.yValues[i] + '\n';
    }

    var encodedUri = encodeURI(exportArrayString);
    window.open(encodedUri);
  };

  $scope.getXLabels = function(){
    var tempHeader = ",";
    for (var i = 0; i < $scope.plotlyData.xValues.length; i++) {
      tempHeader += $scope.plotlyData.xValues[i] + ",";
    }

    return tempHeader;
  };

  $scope.getYLabels = function(){
    var tempHeader = ",";
    for (var i = 0; i < $scope.plotlyData.yValues.length; i++) {
      tempHeader += $scope.plotlyData.yValues[($scope.plotlyData.yValues.length - 1) - i] + ",";
    }

    return tempHeader;
  };


  $scope.init_page = function(){ //http://localhost:63343/Prototype2/prototype2C.html#?savedId=563a8343f6f4071f79300231
    $('#heatmapIsLoading').html('<span class="fa fa-spinner fa-2x fa-pulse"></span>');
    var myPlot = document.getElementById('heatmap')
    var heatmap_title = "";
    $scope.esId = $scope.GetQueryStringParams("clusterId");
    $scope.title = $scope.GetQueryStringParams("termId").replace("%20", " ");
    $scope.plotlyData.isFullSize = $scope.GetQueryStringParams("showFullSize");
    if(typeof $scope.plotlyData.isFullSize === 'undefined'){
      $scope.plotlyData.isFullSize = false;
    } else {
      $scope.plotlyData.isNewWindow = true;
    }

    var url = $scope.pythonHost + "/nav/elasticsearch/getheatmap3/" + $scope.esId + "?callback=JSON_CALLBACK";
    console.log(url);
    $('#heatmap').css( "display", "none" );
    var myrequest = HttpServiceJsonp.jsonp(url)
         .success(function (result) {
           //$('#heatmapIsLoading').html('<h4>Cluster - ' + $scope.title + '</h4>');
           $('#heatmapIsLoading').html('');

           //===========================================
           // calculate the full size height and width
           //===========================================
           $scope.plotlyData.heatmapFullHeight = 22 * result.yValues.length + 180;
           $scope.plotlyData.heatmapFullWidth = 22 * result.xValues.length + 100;

           if($scope.plotlyData.isFullSize){
             height = $scope.plotlyData.heatmapFullHeight;
             width = $scope.plotlyData.heatmapFullWidth;
           } else {
             height = $scope.plotlyData.heatmapScaledHeight;
             width = $scope.plotlyData.heatmapScaledWidth;
           }

           $('#heatmap').width(width).height(height);

           $scope.plotlyData.xValues = result.xValues;
           $scope.plotlyData.yValues = result.yValues;
           $scope.plotlyData.zValues = result.zValues;

           var colorscaleValue = [
             [0, '#ee4035'],
             [1, '#0392cf']
           ];

           var data = [{
             x: $scope.plotlyData.xValues,
             y: $scope.plotlyData.yValues,
             z: $scope.plotlyData.zValues,
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

           $scope.plotlyData.passThisDataAlong = data;
           $scope.passThisLayoutAlong = layout;

           Plotly.newPlot('heatmap', data, layout, {showLink: false});
           //Plotly.addTraces('heatmap', {y: [1, 5, 7]}, 0);

/*
           $('#heatmap').on('plotly_click', function(myData){
             var plotDiv = document.getElementById('heatmap');
              console.log(plotDiv.data);
              console.log(myData.target._hoverdata[0].y);

              if ($scope.$root.$$phase != '$apply' && $scope.$root.$$phase != '$digest') {
                $scope.$apply(function(){
                  $scope.plotlyData.exportRowTarget = myData.target._hoverdata[0].y;
                  $scope.plotlyData.exportColumnTarget = myData.target._hoverdata[0].x;
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
  };
});

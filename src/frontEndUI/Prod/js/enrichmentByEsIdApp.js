
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
      //$scope.pythonHost = "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com"; // PROD
  //$scope.pythonHost = "http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com"; //Search Engine (Dev)
  //$scope.pythonHost = "http://ec2-52-24-205-32.us-west-2.compute.amazonaws.com:8181"; //Search Engine (Prod)
  $scope.pythonHost = python_host_global;

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

    $scope.init_page = function(){ //http://localhost:63343/Prototype2/prototype2C.html#?savedId=563a8343f6f4071f79300231
      var esId = GetQueryStringParams("clusterId");

      var url = $scope.pythonHost + "/api/elasticsearch/getclusterenrichmentbyid/" + esId + "?callback=JSON_CALLBACK";
      var myrequest = HttpServiceJsonp.jsonp(url)
           .success(function (result) {
                $scope.modalData = result;
           }).finally(function () {
      }).error(function (data, status, headers, config) {
          alert(data + ' - ' + status + ' - ' + headers);
      });

    };




});

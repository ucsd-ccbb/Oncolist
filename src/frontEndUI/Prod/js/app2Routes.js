var module = angular.module("sampleApp", ['ngRoute']);

module.config(['$routeProvider',
    function($routeProvider) {
        $routeProvider.
            when('/route1', {
                templateUrl: 'angular-route-template-1.html',
                controller: 'RouteController'
            }).
            when('/route2', {
                templateUrl: 'angular-route-template-2.jsp',
                controller: 'RouteController'
            }).
            otherwise({
                redirectTo: '/'
            });
    }]);

module.controller("myCtrl", function($scope) {

});

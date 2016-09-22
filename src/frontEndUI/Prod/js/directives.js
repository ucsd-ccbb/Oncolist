angular.module('directives', [])

.directive('loading', function() {
  return {
    restrict: 'AE',
    scope: {
      request: '=',
      message: '@',
      inline: '@'
    },
    templateUrl: '/static/common/html/loading.html'
  };
})


.directive( 'editInPlace', function($log) {
    return {
        restrict: 'AE',
        scope: {
            value: '=',
            onBlur: '&',
            placeholder: '@',
            default: '@'
        },
        template: '<a href="" ng-click="edit()">{{display()}} <small><i class="fa fa-edit text-muted-light"></i></small></a><input type="text" class="form-control inline" ng-model="value" ng-blur="blur()" placeholder="{{placeholder}}" ng-keyup="$event.keyCode == 13 ? blur() : null" style="width: auto; height: 2em"/>',
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
            };

            // blur handler removes active state and calls user onBlur callback
            $scope.blur = function() {
                element.removeClass('active');
                if ($scope.clean != $scope.value) {
                    $scope.onBlur();
                }
            };
        }
    };
})

;
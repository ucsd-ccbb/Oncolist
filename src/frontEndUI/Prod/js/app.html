var app = angular.module('plunker', ['siyfion.sfTypeahead']);

app.controller('MainCtrl', function($scope) {
  
  $scope.selectedNumber = null;
  
  // instantiate the bloodhound suggestion engine
  var numbers = new Bloodhound({
    datumTokenizer: function(d) { return Bloodhound.tokenizers.whitespace(d.num); },
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    local: [
      { num: 'one' },
      { num: 'two' },
      { num: 'three' },
      { num: 'four' },
      { num: 'five' },
      { num: 'six' },
      { num: 'seven' },
      { num: 'eight' },
      { num: 'nine' },
      { num: 'ten' }
    ]
  });
   
  // initialize the bloodhound suggestion engine
  numbers.initialize();
  
  $scope.numbersDataset = {
    displayKey: 'num',
    source: numbers.ttAdapter()
  };
  
  $scope.addValue = function () {
    numbers.add({
      num: 'twenty'
    });
  };
  
  $scope.setValue = function () {
    $scope.selectedNumber = { num: 'seven' };
  };
  
  $scope.clearValue = function () {
    $scope.selectedNumber = null;
  };

  
  // Typeahead options object
  $scope.exampleOptions = {
    highlight: true
  };
  
  $scope.exampleOptionsNonEditable = {
    highlight: true,
    editable: false // the new feature
  };
  
});

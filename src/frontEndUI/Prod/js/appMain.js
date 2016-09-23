var app = angular.module('myApp', ['ngRoute', 'services', 'angular-clipboard','angular-szn-autocomplete', 'rzModule']); //ui-bootstrap

var useLocalHost = false;

var cy;

var historySize = 0;

app.config(['$routeProvider',


    function ($routeProvider) {
        $routeProvider
        .when('/main-about', {
            templateUrl: 'partials/about/mainAboutTemplate.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/condition-about', {
            templateUrl: 'partials/about/conditionsAboutTemplate.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/drug-about', {
            templateUrl: 'partials/about/drugsAboutTemplate.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/gene-module-about', {
            templateUrl: 'partials/about/geneModulesAboutTemplate.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/harvesting-about', {
            templateUrl: 'partials/about/harvestingAboutTemplate.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/disease-disease-distance', {
            templateUrl: 'partials/about/diseaseDiseaseDistance.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/disease-disease-mirna', {
            templateUrl: 'partials/about/diseaseDiseaseMiRna.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/multipurpose-genes', {
            templateUrl: 'partials/about/multipurpose_genes.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/search-analysis', {
            templateUrl: 'partials/about/searchAnalysisAbout.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/author-about', {
            templateUrl: 'partials/about/authorsAboutTemplate.html',
            controller: 'resultsController',
            activetab: 'MAINABOUT'
        })
        .when('/gene-search-results', {
            templateUrl: 'partials/gene-search-results.html',
            controller: 'resultsController',
            activetab: 'GENES'
        })
        .when('/variant-search-results', {
            templateUrl: 'partials/variant-search-results.html',
            controller: 'resultsController',
            activetab: 'VARIANT'
        })
        .when('/pathway-search-results', {
            templateUrl: 'partials/searchTabs/pathways-search-results.html',
            controller: 'resultsController',
            activetab: 'PATHWAYS'
        })
        .when('/phenotype-search-results', {
            templateUrl: 'partials/searchTabs/phenotype-search-results.html',
            controller: 'resultsController',
            activetab: 'PHENOTYPES'
        })
        .when('/people-search-results', {
            templateUrl: 'partials/searchTabs/people-search-results.html',
            controller: 'resultsController',
            activetab: 'PEOPLE_GENE'
        })
        .when('/drug-search-results', {
            templateUrl: 'partials/searchTabs/drug-search-results.html',
            controller: 'resultsController',
            activetab: 'DRUG'
        })
        .when('/other-clusters-results', {
            templateUrl: 'partials/other-clusters-results.html',
            controller: 'resultsController',
            activetab: 'OTHER_CLUSTERS'
        })
        .when('/gene-by-genome-search-results', {
            templateUrl: 'partials/searchTabs/gene-by-genome-search-results.html',
            controller: 'resultsController',
            activetab: 'TEST1'
        })
        .when('/heatmap-results/:title/:map_id/:matrix_size', {
            templateUrl: 'partials/D3HeatMap.html',
            controller: 'resultsController',
            activetab: 'HEATMAP'
        })
        .when('/information', {
            templateUrl: 'partials/information.html',
            controller: 'myCtrl'
        })
        .when('/:querystring', {
            controller: 'myCtrl'
        })
        .when('/cytoscape/:id', {
            templateUrl: 'partials/cytoscape.html',
            controller: 'resultsController',
            activetab: 'CYTOSCAPE'
        })
        .otherwise({
            redirectTo: '/main-about'
        });
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

app.filter('groupBy', function() {
    return _.memoize(function(items, field) {
        return _.groupBy(items, field);
    }
    );
});

app.filter('toArray', function() { return function(obj) {
    if (!(obj instanceof Object)) return obj;
    return _.map(obj, function(val, key) {
        return Object.defineProperty(val, '$key', {__proto__: null, value: key});
    });
}});

app.factory("searchResults",function(){
    return {};
});

app.filter('capitalize', function() {
    return function(input) {
      return (!!input) ? input.charAt(0).toUpperCase() + input.substr(1).toLowerCase() : '';
    }
});

app.controller( "aboutCtrl",function($scope, HttpServiceJsonp, searchResults, $routeParams){

  $scope.about = {
     //pythonHost = "http://localhost:8182", // Localhost
         //pythonHost = "http://ec2-52-26-26-232.us-west-2.compute.amazonaws.com", // PROD
     //pythonHost: "http://ec2-52-32-253-172.us-west-2.compute.amazonaws.com", //Search Engine (Dev)
     //pythonHost: "http://ec2-52-38-59-248.us-west-2.compute.amazonaws.com", //Search Engine (Dev) REST WEB ES
     pythonHost: python_host_global, //use variable from env.js

     showMore: {
       topGeneSearch: []//searchResults.pageStats
     }
   };

   $scope.init_page = function(){
     if(!searchResults.aboutInit){
       searchResults.aboutInit = true;

       var url = $scope.about.pythonHost + "/api/get/search/stats?callback=JSON_CALLBACK";
       var myrequest = HttpServiceJsonp.jsonp(url)
       .success(function (result) {
           searchResults.pageStats = result;
           $scope.about.showMore.topGeneSearch = result;
       }).finally(function () {
       }).error(function (data, status, headers, config) {
           alert(data + ' - ' + status + ' - ' + headers);
       });
     } else {
       $scope.about.showMore.topGeneSearch = searchResults.pageStats;
     }
   };

   $scope.init_page();

});

function popupClick(selection) {
    alert('selection: ' + selection);
}


document.addEventListener('copy', function (e) {
    if($("#copySwitch").is(":checked")){

        var textToPutOnClipboard = "SMAD9,SULT1C4,KIRREL,PDZD2,HTR1B,RP1L1,PCDHGB7";
        //var textToPutOnClipboard = "ENSG00000277494,OR2J3,AANAT,KRT80,lymphatic,MACC1,LOC400794,LOC139201,CCDC158,PLAC8L1,caffeine,CLK1,Cholera,GLTP,PITPNM2,TRAPPC8,EIF2S2,adverse,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,transplanted,CNOT7,STK39,CAPZA1,STIM2,nasal,DLL4,WEE1,MYO1D,TEAD3";
    }
});

$(document).ready(function() {
    rescale();
});

function rescale(){
    var size = {width: $(window).width() , height: $(window).height() }

    /*CALCULATE SIZE*/
    var offset = 12;
    var widthOffset = 0;
    var offsetBody = 95;

    //$('#myClusterModal').css('height', size.height - offset );
    $('#myClusterModal').css('width', size.width - widthOffset);
    $('#myClusterModalBody').css('height', size.height - offset - 66 );
    $('#myClusterModalBodyx').css('height', size.height - offset - 68 );
    $('#drugsModalBody').css('height', size.height - offset - 63 );


    $('#myModal').css('height', size.height - offset);
    $('#myModal').css('width', size.width + widthOffset);
    $('#myModalBody').css('height', size.height - offset - 56 );
    //$('#myClusterModalBody').css('width', size.width - widthOffset);
    //$('#myModalDialog').css('height', size.height - offset);

    //$('#myClusterModal').css('height', size.height - offset);
    //$('#myClusterModal').css('width', size.width + widthOffset);


    //$('.modal-body').css('height', size.height - offsetBody);
    //$('.modal-body').css('width', size.width - 10);
    //$('.modal-body').css('height', size.height - (offset + offsetBody));
    $('#myClusterModal').css('top', 0);
    $('#myModal').css('top', 0);
    //console.log(size);
}
$(window).bind("resize", rescale);

function confirmClick(e) {
  //alert(window.history.length + '  other: ' + historySize);
  window.history.back();
  if (!e)
      e = window.event;

  //IE9 & Other Browsers
  if (e.stopPropagation) {
    e.stopPropagation();
  }
  //IE8 and Lower
  else {
    e.cancelBubble = true;
  }

};

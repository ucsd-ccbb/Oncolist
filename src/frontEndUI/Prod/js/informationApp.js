
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
  console.log("in infoapp.js");
  $scope.pythonHost = python_host_global;
  $scope.info = {"TermId": "",
    "termDescription": "",
    "termEntrezDescription": "",
    "currentTab": "unknown",
    "activateDrugbank": false,
    "activateGenecard": false,
    "phenotype_info": [],
    "snps": "",
    "people_publications": [],
    "showMorePublications": false,
    "tissue": "",
    "termId": "",
    "title": "",
    "condition": "",
    "variants": [],
    "pubmedIds": [],
    "cosmicIds": []
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

    $scope.init_page = function(){ //http://localhost:63343/Prototype2/prototype2C.html#?savedId=563a8343f6f4071f79300231
       var termId = GetQueryStringParams('termId');
       $scope.info.termId = termId;
       var currentTab = GetQueryStringParams('currentTab');

       var title = GetQueryStringParams('title');
       $scope.info.title = title;
       //$scope.info.termDescription = GetQueryStringParams('termDesc');
       //if($scope.info.termDescription.length > 0){
        // $scope.info.termDescription = $scope.info.termDescription.replace(/%20/g, " ");
       //}

       if(currentTab === 'GENE'){
         $scope.info.activateGenecard = true;
         $scope.info.activateDrugbank = false;
         $scope.info.currentTab = "GENE";

         var snps = GetQueryStringParams('snps');
         if(snps.length > 0){
           snps = snps.replace(/%3E/g, ">");
           snpsArray = snps.split(',');
           $scope.info.snps = snpsArray;

         }

//         geneUrl = $scope.pythonHost + "/api/elasticsearch/getauthorcenteredbyid/" + $scope.info.elasticId  + "/" + genes  + "?callback=JSON_CALLBACK";

//         HttpServiceJsonp.jsonp(geneUrl)
//         .success(function (result) {
//           $scope.info.people_publications = result["publications"];
//         }).finally(function () {
//         }).error(function (data, status, headers, config) {
//             alert(data + ' - ' + status + ' - ' + headers);
//         });


     } else if(currentTab === 'CONDITION_GENE'){
            $scope.info.activateGenecard = true;
            $scope.info.activateDrugbank = false;
            $scope.info.currentTab = "CONDITION_GENE";

            var condition = GetQueryStringParams('condition');
            if(condition.length > 0){
              condition = condition.replace(/%20/g, " ");
              $scope.info.condition = condition;
            }

            var tissue = GetQueryStringParams('tissue');
            if(tissue.length > 0){
                tissue = tissue.replace(/%20/g, " ");
                $scope.info.tissue = tissue;
            }

            geneUrl = $scope.pythonHost + "/api/conditions/genevariants/" + termId + "/" + $scope.info.condition + "/" + $scope.info.tissue + "?callback=JSON_CALLBACK";

            HttpServiceJsonp.jsonp(geneUrl)
            .success(function (result) {
              $scope.info.variants = result;
            }).finally(function () {
            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });


      } else if(currentTab === 'DRUG'){
         $scope.info.currentTab = "DRUG";
         $scope.info.activateGenecard = false;
         $scope.info.activateDrugbank = true;
         $scope.info.drugbank_id = GetQueryStringParams('dbId');
      } else if(currentTab === 'DRUG_GENE'){
         $scope.info.currentTab = "DRUG_GENE";
         $scope.info.activateGenecard = true;
         $scope.info.activateDrugbank = false;
         $scope.info.drugbank_id = GetQueryStringParams('dbId');
       } else if(currentTab === 'PEOPLE_GENE'){
         $scope.info.currentTab = "PEOPLE_GENE";

         var author = GetQueryStringParams('author');
         var genes = GetQueryStringParams('genes');
         if(author.length > 0 && genes.length > 0){
           //genesUrlQueryString = ""
           //genesArray = genes.split(',');

           //(Wang, Ying[Author - Full]) AND (WEE1[Title/Abstract] OR STK39[Title/Abstract] OR FOSB[Title/Abstract] OR GPIHBP1[Title/Abstract])
           //for(var i=0; i< genesArray.length; i++){
            // if(i === genesArray.length - 1) {
            //   genesUrlQueryString += genesArray[i] + "[Title/Abstract]";
             //} else {
            //   genesUrlQueryString += genesArray[i] + "[Title/Abstract]%20OR%20";
            // }
           //}

           //$scope.info.pubmedUrl = "http://www.ncbi.nlm.nih.gov/pubmed?term=(" + author + "[Author%20-%20Full])%20AND%20(" + genesUrlQueryString + ")"

           //alert($scope.info.pubmedUrl);
           author = author.replace("%20", " ");
           author = author.replace("%27", "''");
           $scope.info.elasticId = GetQueryStringParams('ElasticId');

           //peopleUrl = $scope.pythonHost + "/api/get/people/gene/targeted/" + author + "/" + genes  + "?callback=JSON_CALLBACK";
           peopleUrl = $scope.pythonHost + "/api/elasticsearch/getauthorcenteredbyid/" + $scope.info.elasticId  + "/" + genes  + "?callback=JSON_CALLBACK";

           HttpServiceJsonp.jsonp(peopleUrl)
               .success(function (result) {
                 $scope.info.people_publications = result["publications"];
               }).finally(function () {
               }).error(function (data, status, headers, config) {
                   alert(data + ' - ' + status + ' - ' + headers);
               });
         }
         $scope.info.activateGenecard = false;
         $scope.info.activateDrugbank = true;
       } else if(currentTab === 'PEOPLE'){
         $scope.info.currentTab = "PEOPLE";

         $scope.info.activateGenecard = false;
         $scope.info.activateDrugbank = true;
       } else if(currentTab === 'PATHWAYS'){
          $scope.info.currentTab = "PATHWAYS";

       } else if(currentTab === 'PHENOTYPE'){
/*        $scope.info.currentTab = "PHENOTYPE";
        $scope.info.elasticId = GetQueryStringParams('ElasticId');
        //author = author.replace("%20", " ");

        if($scope.info.elasticId != "unknown"){
          url = $scope.pythonHost + "/nav/elasticsearch/getclinvar/" + $scope.info.elasticId  + "?callback=JSON_CALLBACK";
          HttpServiceJsonp.jsonp(url)
            .success(function (result) {
              $scope.info.phenotype_info = result;
            }).finally(function () {
            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });
        } else {
          $scope.info.phenotype_info = {'Phenotype_ids': [{'url': 'http://www.google.com/search?q=' + termId, 'type': 'Goo', 'title': 'Google search (opens in new window)'}]};
        }
        */
    } else if(currentTab === 'CONDITION'){
        $scope.info.currentTab = "CONDITION";
        var pubmedIds = GetQueryStringParams('pubmedIds');

        $scope.info.pubmedIds = pubmedIds.split(",");
        if($scope.info.pubmedIds.length > 0){
            if($scope.info.pubmedIds[0].trim().length < 1){
                $scope.info.pubmedIds = [];
            }
        }

        var cosmicIds = GetQueryStringParams('cosmicIds');
        $scope.info.cosmicIds = cosmicIds.split(",");

        if($scope.info.cosmicIds.length > 0){
            if($scope.info.cosmicIds[0].trim().length < 1){
                $scope.info.cosmicIds = [];
            }
        }

        var genes = GetQueryStringParams('genes');
        $scope.info.genes = genes.split(",");

        if($scope.info.genes.length > 0){
            if($scope.info.genes[0].trim().length < 1){
                $scope.info.genes = [];
            }
        }
      } else {
         $scope.info.activateGenecard = false;
         $scope.info.activateDrugbank = false;
       }

      $scope.info.termId = termId.replace(/%20/g, " ");

      if($scope.info.termId != "INVALIDGENE"){
          url = $scope.pythonHost + "/nav/term/lookup/" + $scope.info.termId  + "?callback=JSON_CALLBACK";

          HttpServiceJsonp.jsonp(url)
          .success(function (result) {
            if(result["termClassification"].length > 0) {
              $scope.info.termDescription = result["termClassification"][0]["desc"]
              $scope.info.termEntrezDescription = result["entrez_summary"]
            }
          }).finally(function () {
          }).error(function (data, status, headers, config) {
              alert(data + ' - ' + status + ' - ' + headers);
          });
      } else {
          $scope.info.termDescription = $scope.info.title;
          $scope.info.termId = $scope.info.title;
      }
    };
});

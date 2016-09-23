var app = angular.module('myApp'); //ui-bootstrap


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

app.controller('myCtrl', function ($scope, $http, $window, $log, $filter, HttpServiceJsonp, ClusterSearchService, ConditionSearchService, AuthorSearchService, DrugSearchService, InferredDrugSearchService, Icd10Search, $routeParams, searchResults, $rootScope, $location, $route, $timeout) {
    $scope.useDev = false;
    $scope.searchbox = "OR2J3, AANAT, CCDC158, PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,ST14,NXF1,H3F3B, FOSB, MTMR4, USP46, CDH11, ENAH, CNOT7, STK39, CAPZA1, STIM2, DLL4, WEE1, MYO1D, TEAD3";
    $scope.searchResultsWithGroups = [];
    searchResults.searchResultsWithGroups = [];
    searchResults.info = {
      esIdInputVal: "default"
    };

    $scope.bridgeService = searchResults;

    $scope.pythonHost = python_host_global; //use variable from env.js
    $scope.webServerHost = "http://geneli.st";

    $scope.lastKey = '';
    $scope.previousLastKey = '';
    $scope.showTerms = true;
    $scope.cytoObjElements = [];
    $scope.dynamicPopover = "";
    filter:startFilter = "";
    $scope.showFocus = true;
    $scope.pathwayResults = [];
    $scope.currentTab = "PATHWAYS";
    $scope.currentSubTab = "PEOPLE";
    $scope.networkResult = [];
    $scope.networkViewItems = [];
    $scope.directSearch = false;
    $scope.loading = false;
    $scope.pathwaysRespHits = [];
    $scope.tabWasClicked = [];
    $scope.hoverValue = "";
    $scope.showMore = {
      'genes': false,
      'pathways': false,
      'drugs': false,
      'phenotypes': false,
      'proteins': false,
      'diseases': false,
      'genomes': false,
      'unknowns': false,
      'enrichment': false,
      'smallScreen': true,
      'genesTabCount': 0,
      'clustersTabCount': 0,
      'conditionsTabCount': 0,
      'authorsTabCount': 0,
      'drugsTabCount': 0,
      'filterOverlap': false,
      'resultsPaneHeight': 600,
      'counts': {},
      'topGeneSearch': [],
      'clusterFilteredAnnotations': [],
      'permaClusterFilteredAnnotations': [],
      'drugGeneFilter': [],
      'permaDrugGeneFilter': [],
      'authorGeneFilter': [],
      'permaAuthorGeneFilter': [],
      'conditionsFilter': [],
      'permaConditionsFilter': [],
      'tissuesFilter': [],
      'permaTissuesFilter': [],
      'clusterFilteredDiseases': [],
      'permaClusterFilteredDiseases': [],

      'clusterFilteredMatrixType': [],
      'permaClusterFilteredMatrixType': [],
      //'clusterFilteredMatrixType': ["mirna vs mutation","mirna vs rnaseq","mutation vs mutation","rnaseq vs mutation","rnaseq vs rnaseq","mirna vs mirna"],
      //'permaClusterFilteredMatrixType': ["mirna vs mutation","mirna vs rnaseq","mutation vs mutation","rnaseq vs mutation","rnaseq vs rnaseq","mirna vs mirna"],
      'clusterAnnotationGOIds': [],
      'linkCopied': false,
      'filteredItemsTotal': 0,
      'filterState': "PAGED",
      'filterConditionState': "PAGED",
      'filterAuthorState': "PAGED",
      'filterDiseases': true,
      'filterDiseasesLimit': 4,
      'filterAnnotations': true,
      'filterAnnotationsLimit': 4,
      'filterMatrix': true,
      'filterMatrixLimit': 4,
      'filterConditions': true,
      'filterConditionsLimit': 4,
      'filterTissuesLimit': 4
    };

    $scope.showAbout = "MAIN";

    $scope.info = {
        windowWidth: 0,
        windowHeight: 0,
        esIdInputVal: "",
        showAbout: "MAIN"
    };

    $scope.minRangeSlider = {
       minValue: 30,
       maxValue: 70,
       options: {
         floor: 0,
         ceil: 100,
         step: 1,
         minRange: 0,
         maxRange: 100
       }
     };

    $scope.clusters = {
        "hit_ids": "",
        'inferred_drug_cluster_ids': "",
        'inferred_drug_cluster_ids_with_disease': []
    };

    $scope.drugs = {
        'inferred_drugs': []
    };

    $scope.showTermWarning = false;
    $scope.showSearchWarning = false;
    $scope.showMaxWarning = false;
    $scope.rangeSlider = {'val': 0.0};
    $scope.rangeSliderGO = {'val': 0};
    $scope.dynamicPopover = {
        content: '<form><a onclick="alert();" href="#">Click me</a></form>',
        templateUrl: 'myPopoverTemplate.html',
        title: 'Select Term Type'
    };
    $scope.$route = $route;
    $scope.log=[];

    $scope.showgraphSidebar = false;
    $scope.toggleSidebar = function() {
        $scope.showgraphSidebar = !$scope.showgraphSidebar;
    }

    $scope.tutorialItems = [
/*        {
            "title": "How do I perform a single gene search?",
            "searchType": "SINGLE",
            "instructions": "To perform a single gene search enter a gene in the search box above or copy and paste from the text below",
            "termsList": "BRCA1",
            "termsList2": "",
            "tab": "GENES"
        },
        */
        {
            "title": "How do I search with multiple genes?",
            "searchType": "MULTIPLE",
            "instructions": "To perform a basic search one or more genes can be typed into the search box above or copied from the list below and pasted",
            "termsList": "NDUFA2 NAPG IL1RAP ENSG00000262599 NKD2 CNTD1 PSPC1 C16ORF13 ENSG00000146676 ENSG00000145287 ENSG00000257950 SH2B2 ZNF146 AGK MRAS",
            "termsList2": "",
            "tab": "GENES"
        },
/*        {
            "title": "How do I narrow my search to one disease type?",
            "searchType": "DISEASE",
            "instructions": "To narrow your search to one disease type is easy.  Just add a disease term to your search.  ",
            "termsList": "ST6GALNAC5 TRIO TNS3 TRAPPC2 CAV2 IFI27 PID1 SNX brain lower grade glioma",
            "termsList2": "",
            "tab": "GENES"
        },
        */
        {
            "title": "How do I add more search genes to my query?",
            "searchType": "ADDTERMS",
            "instructions": "You can add additional genes to your query by simply adding them in the textbox.  Each additional search term is combined with your previous search until you clear the search.",
            "termsList": "Search with these terms first: CCDC19 C6orf221 DNAJB6 PTPRS MTMR15 SEMA3G DCLK2 ZNF777 ADARB2 KRTAP25-1 HS2ST1 TPO SNED1",
            "termsList2": "After the search results appear add another search term in the textbox and click the search button",
            "tab": "GENES"
        }
    ]

    $scope.getMyImage = function(){

      url = $scope.pythonHost + "/api/getImage?callback=JSON_CALLBACK";
      //alert(urlstar);

      HttpServiceJsonp.jsonp(url)
      .success(function (result) {
        $("#myImageGoesHere").html("<img src='http://localhost:3000/images/" + result["imagename"] + "' />");

      }).finally(function () {
      }).error(function (data, status, headers, config) {
          alert(data + ' - ' + status + ' - ' + headers);
      });//http://localhost:63343/Prototype2/prototype2C.html#?savedId=563aa16bf6f407214c72cbe1

    };


    //================================
    // DELETE THIS!  DELETE THIS!
    //================================
    $scope.setClusterIFrameContent = function(setThisParm) {
      $('#myClusterViz').html("<iframe src='about:blank' width='100%' height='600' style='overflow-x: hidden; overflow-y: hidden;' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
      $scope.showMore.enrichment = false;
      var termIdTitle = "My Title";
      console.log('Delete This');

      if(termIdTitle.length > 35) {
        termIdTitle = termIdTitle.substring(0, 34) + "...";
      }
      var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";

      $('#myModalLabel').html(modalTitle);

      $timeout(function() {
        $("#myClusterViz").find('iframe').attr('src',"partials/" + setThisParm); //
      }, 200);

      //$('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
      //  $(this).find('iframe').attr('src',setThisParm);
      //});

    };
    //================================
    // END DELETE THIS!  DELETE THIS!
    //================================

    $scope.showlinkCopiedAlert = function(){
        $scope.showMore.linkCopied=true;
        $timeout(function() {
            $scope.showMore.linkCopied=false;
        }, 1000);
    }

    $scope.setClusterIFrameLocal = function(setThisParm, setOverlap) {
        var url = setThisParm + searchResults.info.esIdInput + "&geneList=";
        if(setOverlap){
            url += searchResults.info.overlap;
        } else {
            url += "INVALIDGENE";
        }
      // //alert("partials/" + url)
      //console.log("url: " + url);
      //console.log(searchResults);
      $('#myClusterModalBody').html("<iframe width='100%' height='" + searchResults.info.winHeight + "' style='overflow-x: hidden; overflow-y: hidden;' frameborder='0' allowtransparency='true' src='partials/" + url + "' id='myIFrame' name='contentframe'></iframe>");
      //$('#myClusterModalBody').html("<iframe width='100%' height='600' style='overflow-x: hidden; overflow-y: hidden;' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");


      //$timeout(function() {
    //    $("#myClusterModalBody").find('iframe').attr('src',"partials/" + setThisParm);
    //}, 400);

    };

    $scope.showEnrichmentInModal = function(setThisParm) {

      //http://localhost:63343/Prototype2/partials/enrichmentByEsId.html?clusterId=AVK9E34rAo6qI1oq2att
      var url = setThisParm + searchResults.info.esIdInput;
      //var url = "partials/enrichmentByEsId.html?clusterId=" + searchResults.info.esIdInput;
      $('#myClusterModalBody').html("<iframe width='100%' height='600' frameborder='0' allowtransparency='true' src='" + url + "' id='myIFrame' name='contentframe'></iframe>");
//      $scope.showMore.enrichment = true;

//      var myrequest = HttpServiceJsonp.jsonp(url)
//           .success(function (result) {
//                $scope.modalData = result;
//           }).finally(function () {
//      }).error(function (data, status, headers, config) {
//          alert(data + ' - ' + status + ' - ' + headers);
//      });
    };

    $scope.changeFunction=function(){
        $scope.log.push('Called');
    };

    $scope.items = [{
      name: "Gene info goes here"
    }, {
      name: "lorem ipsum"
    }, {
      name: ""
    }];

    $scope.query = [
        { label: 'Joe'},
        { label: 'Mike'},
        { label: 'Diane'}
    ];

    $scope.getAutocompleteResults = function (query, deferred) {
    //var url = "http://jkuchta.cz/wikisearch/?action=query&list=search&srsearch=intitle:" + query + "&format=json&srprop=snippet&continue&srlimit=10";

    var clean_query = query
    if(clean_query.indexOf("JSON_CALLBACK") > -1){
        clean_query = clean_query.replace(/JSON_CALLBACK/g, "");
    }
    clean_query = clean_query.replace(/\//g, "");
    clean_query = clean_query.replace(/\?/g, "");

    var url = $scope.pythonHost + "/nav/terms/autocomplete/" + clean_query + "?callback=JSON_CALLBACK";

    HttpServiceJsonp.jsonp(url)
    .success((function (deferred, data) { // send request
            // format data into desired structure
      var results = [];
            //data.query.search.forEach(function (item) {
            data.termClassification.forEach(function (item) {
                if(item.geneSymbol != undefined && item.geneSymbol != item.term){
                    results.push({value: item.term + '~' + item.type + '~' + item.geneSymbol});
                } else {
                    if(item.type === "ICD10"){
                      results.push({value: item.term + '~PHENOTYPE'});
                  } else if (item.type === "DISEASE") {
                      results.push({value: item.term + '~' + item.type + '~' + item.group});
                  } else {
                      results.push({value: item.term + '~' + item.type});
                    }
                }
            });

            // resolve the deferred object
      deferred.resolve({results: results});
    }).bind(this, deferred));

  };

    $scope.auto_complete_selected = function(selectedValue){
      if(selectedValue.value.indexOf("HSA-") > -1){
          reassemble = selectedValue.value.split("~");
          if(reassemble.length > 1){
            $scope.add_terms_from_autocomplete(reassemble[0].toLowerCase() + "~" + reassemble[1]);
          }
      }
      else {
        $scope.add_terms_from_autocomplete(selectedValue.value);
      }

      //angular.element('#clear_search').trigger('click');

      $scope.dirty.term_list = [];
      $scope.$apply()
      //$("#gene-list-input").value = "";
    }

    $scope.add_terms_from_autocomplete = function(term){
      term_info = term.split('~');

      var term = null;
      if(term_info.indexOf("PHENOTYPE") > -1) {
        term = {'user': term_info[0], 'termTitle': term_info[0], "type": "icd10"};
    } else if (term_info.indexOf("DISEASE") > -1) {
        term = {'user': term_info[2], 'termTitle': term_info[0], "type": term_info[1].toLowerCase()};
    } else {
        term = {'user': term_info[0], 'termTitle': term_info[0], "type": term_info[1].toLowerCase()};
      }
      //$scope.project.gene_list.push(term);
      $scope.project.gene_list.unshift(term);
      $scope.project.term_list.unshift(term);
      $scope.ArrangeTerms();
    };

    $scope.useDefaultSearch = function(){
      //$scope.dirty.term_list = "SMAD9,SULT1C4,KIRREL,PDZD2,HTR1B,RP1L1,PCDHGB7";
      $scope.dirty.term_list = "ENSG00000277494,OR2J3,AANAT,KRT80,MACC1,LOC400794,LOC139201,CCDC158,PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,PNLIP,EHF,FOSB,MTMR4,USP46,CDH11,ENAH,CNOT7,STK39,CAPZA1,STIM2,DLL4,WEE1,MYO1D,TEAD3";//"hsa-mir-21";//
      $scope.lastKey = 13;// force the term resolver to process i.e. simulate that the enter key was pressed
      $scope.add_terms(true);
      $scope.showTermWarning = false;
      $scope.showSearchWarning = false;
    }

    $scope.test10 = function(){
      alert($location.host());
    }

    $scope.tryBasicSearch = function(searchType) {
        if(searchType === 'SINGLE'){
            $scope.dirty.term_list = "BRCA1";
        } else if (searchType === 'MULTIPLE'){
            $scope.dirty.term_list = "NDUFA2 NAPG IL1RAP ENSG00000262599 NKD2 CNTD1 PSPC1 C16ORF13 ENSG00000146676 ENSG00000145287 ENSG00000257950 SH2B2 ZNF146 AGK MRAS";
        } else if (searchType === 'DISEASE'){
            $scope.dirty.term_list = "ST6GALNAC5 TRIO TNS3 TRAPPC2 CAV2 IFI27 PID1 SNX brain lower grade glioma";
        } else if (searchType === 'ADDTERMS'){
            $scope.dirty.term_list = "CCDC19 C6orf221 DNAJB6 PTPRS MTMR15 SEMA3G DCLK2 ZNF777 ADARB2 KRTAP25-1 HS2ST1 TPO SNED1";
        }
        $scope.lastKey = 13;// force the term resolver to process i.e. simulate that the enter key was pressed
        $scope.add_terms(true);
        $scope.showTermWarning = false;
        $scope.showSearchWarning = false;
    };

    $scope.init_page = function(){ //http://localhost:63343/Prototype2/prototype2C.html#?savedId=563a8343f6f4071f79300231
      if($window.innerWidth < 768){
        $scope.showMore.smallScreen = true;
      } else {
        $scope.showMore.smallScreen = false;
      }
      var savedId = $location.search()['savedId'];

      var w = angular.element($window);
      $scope.info.windowWidth = w.width();
      $scope.info.windowHeight = w.height();

      //console.log("h " + w.height());
      //console.log("w " + w.width());

      if(savedId != null){

        url = $scope.pythonHost + "/api/get/saved/search/" + savedId + "?callback=JSON_CALLBACK";

        HttpServiceJsonp.jsonp(url)
            .success(function (result) {
                $scope.dirty.term_list = result.terms;
                $scope.lastKey = 13;// force the term resolver to process i.e. simulate that the enter key was pressed
                $scope.add_terms(true);
                $scope.showTermWarning = false;
                $scope.showSearchWarning = false;
            }).finally(function () {
            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });
      }

    $timeout(function() {
        if($route.current.activetab != "MAINABOUT" && $scope.searchResultsWithGroups.length < 1){
            $location.path('/');
        }
    }, 500);

    };

    $scope.success = function () {
      console.log('Copied!');
    };

    $scope.fail = function (err) {
      console.error('Error!', err);
    };

    $scope.saveSearchState = function(terms_list) {
        //var terms_list = "";
        //for(var i=0; i< $scope.project.term_list.length; i++){
        //  terms_list += $scope.project.term_list[i]["user"] + ",";
        //}

        //if($scope.project.term_list.length > 0){
        //  terms_list = terms_list.substring(0, terms_list.length - 1);
        //}

        if(terms_list.length > 0){
          urlstar = $scope.pythonHost + "/api/save/search/" + terms_list.toUpperCase() + "?callback=JSON_CALLBACK";
          //alert(urlstar);

          HttpServiceJsonp.jsonp(urlstar)
          .success(function (result) {
              $scope.savedSearchId = result.searchId;
            if($location.host() === "localhost"){
                $scope.textToCopy = "http://localhost:3000/#?savedId=" + $scope.savedSearchId;
                //$scope.textToCopy = "http://localhost:63343/Prototype2/prototype2C.html#?savedId=" + $scope.savedSearchId;
            } else if($location.host() === "geneli.st"){
                $scope.textToCopy = "http://geneli.st/#?savedId=" + $scope.savedSearchId;
                //$scope.textToCopy = "http://geneli.st:8181/Prototype2/prototype2C.html#?savedId=" + $scope.savedSearchId;
            } else if($location.host() === "oncolist.org"){
                $scope.textToCopy = "http://oncolist.org/#?savedId=" + $scope.savedSearchId;
                //$scope.textToCopy = "http://geneli.st:8181/Prototype2/prototype2C.html#?savedId=" + $scope.savedSearchId;
            } else {
                $scope.textToCopy = "http://" + $location.host() + ":3000/#?savedId=" + $scope.savedSearchId;
            }

          }).finally(function () {
          }).error(function (data, status, headers, config) {
              alert(data + ' - ' + status + ' - ' + headers);
          });//http://localhost:63343/Prototype2/prototype2C.html#?savedId=563aa16bf6f407214c72cbe1
        }
    };


    //==============================
	//==============================
	//==============================
	//	FILTERS
	//==============================
    //==============================
	//==============================
    $scope.scoreFilter = function (item) {
        if (item.top5) {
            return true;
        } else {
            return true;
        }
    };

    $scope.starFilter = function (item) {
        return item.name.match(/^F*/) ? true : false;


        if(item != $scope.startFilter) {
            return false;
        } else {
            return true;
        }
    };

    $scope.hitOrderFilter = function (item) {
        if(item.searchResultTitle.indexOf(":") > -1) {
                return true;
        }

        if (item.top5) {
            return true;
        } else {
            if (item.hitOrder < $scope.rangeSlider.val) {
                return true;
            } else {
                return false;
            }
        }
    };

    $scope.geneTabFilter = function (item) {
        return item.searchTab === $scope.$route.current.activetab;
    };

    $scope.subTabFilter = function (item) {
        return item.searchTab === $scope.$route.current.activetab;
    };

    $scope.edgeWeightFilter = function (item) {
        return Math.abs(item.weight) > $scope.rangeSlider.val;
    };

    $scope.clusterOverlapFilter = function (item) {
        return item.emphasizeInfoArray.length > 0;
    };

    $scope.clusterOtherAnnotationFilter = function (item) {
        return item.group_title != "Other";
    };

    $scope.geneOverlapFilter = function (item) {
        return item.emphasizeInfoArrayWithWeights.length > 0 || $scope.showMore.filterOverlap;
    };

    $scope.clusterTopQValueFilter = function (item) {
      for(var i=0;i<$scope.showMore.clusterFilteredAnnotations.length;i++){
          if(item.group_title === $scope.showMore.clusterFilteredAnnotations[i]){

            if(item.group_title === "Other"){
                return true;
            } else {
                return item.groupTopQValue >= 0.5;
            }
          }
      }
      return false;
    };

    $scope.clusterMatrixTypeFilter = function (item) {
      for(var i=0;i<$scope.showMore.clusterFilteredMatrixType.length;i++){
          if(item.dataSetType === $scope.showMore.clusterFilteredMatrixType[i]){
              if(item.emphasizeInfoArray.length > 0)
              {
                  if($scope.showMore.clusterFilteredDiseases.indexOf(item.diseaseType) >= 0){
                      return true;
                  }
              }
          }
      }
      return false;
    };

    $scope.drugGeneFilter = function (item) {
      for(var i=0;i<$scope.showMore.drugGeneFilter.length;i++){
          for(var j=0; j<item.emphasizeInfoArrayWithWeights.length; j++){
              var compareThis = item.emphasizeInfoArrayWithWeights[j].name;
              var toThis = $scope.showMore.drugGeneFilter[i];
              if(compareThis === toThis){
                return true;
              }
          }
      }
      return false;
    };

    $scope.authorGeneFilter = function (item) {
      for(var i=0;i<$scope.showMore.authorGeneFilter.length;i++){
          for(var j=0; j<item.emphasizeInfoArray.length; j++){
              var compareThis = item.emphasizeInfoArray[j].gene;
              var toThis = $scope.showMore.authorGeneFilter[i];
              if(compareThis === toThis){
                return true;
              }
          }
      }
      return false;
    };

    $scope.clusterTopQValueFilterList = function (item) {
      if(item.group_title === "Other"){
        return true;
      } else {
        return item.groupTopQValue >= 3.5; // filter value for Q
      }
    };

    $scope.conditionsFilter = function (item) {
      for(var i=0;i<$scope.showMore.conditionsFilter.length;i++){
          if(item.disease === $scope.showMore.conditionsFilter[i]){
              if(item.disease != "NS"){
                  return true;
              }
          }
      }
      return false;
    };

    $scope.tissuesFilter = function (item) {
      for(var i=0;i<$scope.showMore.tissuesFilter.length;i++){
          if(item.tissue === $scope.showMore.tissuesFilter[i]){
              return true;
          }
      }
      return false;
    };

    $scope.setConditionsFilter = function(addThis) {
        var foundMatch = false;
        if($scope.checkConditionFilterState()){
            if($scope.showMore.filterConditionState === "PAGED"){
                console.log("WAS PAGED.  SWITCHED TO NON-PAGED");
                $scope.phenotypeClickPaged(99);
                $scope.showMore.filterConditionState = "NOTPAGED";
            }
        } else if($scope.showMore.filterConditionState === "NOTPAGED"){
            console.log("WAS NON-PAGED.  SWITCHED TO PAGED")
            $scope.phenotypeClickPaged(1);
            $scope.showMore.filterConditionState = "PAGED";
        }

        if($scope.showMore.conditionsFilter.length === $scope.showMore.permaConditionsFilter.length){
            $scope.showMore.conditionsFilter = [];

        }
        for(var i=0;i<$scope.showMore.conditionsFilter.length;i++){
            if(addThis === $scope.showMore.conditionsFilter[i]){
                $scope.showMore.conditionsFilter.splice(i, 1);
                foundMatch = true;
                break;
            }
        }

        if(!foundMatch){
            $scope.showMore.conditionsFilter.push(addThis);
        } else {
            if($scope.showMore.conditionsFilter.length === 0){
                $scope.showMore.conditionsFilter = JSON.parse(JSON.stringify($scope.showMore.permaConditionsFilter));
            }
        }

        //$scope.updateRating();
    }

    $scope.setTissuesFilter = function(addThis) {
        var foundMatch = false;
        if($scope.checkTissueFilterState()){
            if($scope.showMore.filterConditionState === "PAGED"){
                console.log("WAS PAGED.  SWITCHED TO NON-PAGED");
                $scope.phenotypeClickPaged(99);
                $scope.showMore.filterConditionState = "NOTPAGED";
            }
        } else if($scope.showMore.filterConditionState === "NOTPAGED"){
            console.log("WAS NON-PAGED.  SWITCHED TO PAGED")
            $scope.phenotypeClickPaged(1);
            $scope.showMore.filterConditionState = "PAGED";
        }

        if($scope.showMore.tissuesFilter.length === $scope.showMore.permaTissuesFilter.length){
            $scope.showMore.tissuesFilter = [];

        }
        for(var i=0;i<$scope.showMore.tissuesFilter.length;i++){
            if(addThis === $scope.showMore.tissuesFilter[i]){
                $scope.showMore.tissuesFilter.splice(i, 1);
                foundMatch = true;
                break;
            }
        }

        if(!foundMatch){
            $scope.showMore.tissuesFilter.push(addThis);
        } else {
            if($scope.showMore.tissuesFilter.length === 0){
                $scope.showMore.tissuesFilter = JSON.parse(JSON.stringify($scope.showMore.permaTissuesFilter));
            }
        }

        //$scope.updateRating();
    }

    $scope.checkConditionFilterState = function() {
        var conditionFilterCount = $scope.showMore.permaConditionsFilter.length;
        for(var i=0; i<conditionFilterCount; i++){
            if($("#CX" + i).prop("checked")){
                return true;
            }
        }
    };

    $scope.setClusterAnnotationFilter = function(addThis) {
        var foundMatch = false;
        if($scope.checkFilterState()){
            if($scope.showMore.filterState === "PAGED"){
                console.log("WAS PAGED.  SWITCHED TO NON-PAGED");
                $scope.pathwaysClickPaged(99);
                $scope.showMore.filterState = "NOTPAGED";
            }
        } else if($scope.showMore.filterState === "NOTPAGED"){
            console.log("WAS NON-PAGED.  SWITCHED TO PAGED")
            $scope.pathwaysClickPaged(1);
            $scope.showMore.filterState = "PAGED";
        }

        if($scope.showMore.clusterFilteredAnnotations.length === $scope.showMore.permaClusterFilteredAnnotations.length){
            $scope.showMore.clusterFilteredAnnotations = [];

        }
        for(var i=0;i<$scope.showMore.clusterFilteredAnnotations.length;i++){
            if(addThis === $scope.showMore.clusterFilteredAnnotations[i]){
                $scope.showMore.clusterFilteredAnnotations.splice(i, 1);
                foundMatch = true;
                break;
            }
        }

        if(!foundMatch){
            $scope.showMore.clusterFilteredAnnotations.push(addThis);
        } else {
            if($scope.showMore.clusterFilteredAnnotations.length === 0){
                $scope.showMore.clusterFilteredAnnotations = JSON.parse(JSON.stringify($scope.showMore.permaClusterFilteredAnnotations));
            }
        }

        $scope.updateRating();
    }

    $scope.setClusterDiseaseFilter = function(addThis) {
        var foundMatch = false;
        if($scope.checkFilterState()){
            if($scope.showMore.filterState === "PAGED"){
                console.log("WAS PAGED.  SWITCHED TO NON-PAGED");
                $scope.pathwaysClickPaged(99);
                $scope.showMore.filterState = "NOTPAGED";
            }
        } else if($scope.showMore.filterState === "NOTPAGED"){
            console.log("WAS NON-PAGED.  SWITCHED TO PAGED")
            $scope.pathwaysClickPaged(1);
            $scope.showMore.filterState = "PAGED";
        }

        $scope.showMore.filteredItemsTotal = 0;
        if($scope.showMore.clusterFilteredDiseases.length === $scope.showMore.permaClusterFilteredDiseases.length){
            $scope.showMore.clusterFilteredDiseases = [];

        }
        for(var i=0;i<$scope.showMore.clusterFilteredDiseases.length;i++){
            if(addThis === $scope.showMore.clusterFilteredDiseases[i]){
                $scope.showMore.clusterFilteredDiseases.splice(i, 1);
                foundMatch = true;
                break;
            }
        }

        if(!foundMatch){
            $scope.showMore.clusterFilteredDiseases.push(addThis);
        } else {
            if($scope.showMore.clusterFilteredDiseases.length === 0){
                $scope.showMore.clusterFilteredDiseases = JSON.parse(JSON.stringify($scope.showMore.permaClusterFilteredDiseases));
            }
        }
        //console.log($scope.showMore.clusterFilteredDiseases);

        $scope.updateRating();
    }

    $scope.setClusterMatrixTypeFilter = function(addThis) {
        var foundMatch = false;
        if($scope.checkFilterState()){
            if($scope.showMore.filterState === "PAGED"){
                console.log("WAS PAGED.  SWITCHED TO NON-PAGED");
                $scope.pathwaysClickPaged(99);
                $scope.showMore.filterState = "NOTPAGED";
            }
        } else if($scope.showMore.filterState === "NOTPAGED"){
            console.log("WAS NON-PAGED.  SWITCHED TO PAGED")
            $scope.pathwaysClickPaged(1);
            $scope.showMore.filterState = "PAGED";
        }

        if($scope.showMore.clusterFilteredMatrixType.length === $scope.showMore.permaClusterFilteredMatrixType.length){
            $scope.showMore.clusterFilteredMatrixType = [];
        }

        for(var i=0;i<$scope.showMore.clusterFilteredMatrixType.length;i++){
            if(addThis === $scope.showMore.clusterFilteredMatrixType[i]){
                $scope.showMore.clusterFilteredMatrixType.splice(i, 1);
                foundMatch = true;
                break;
            }
        }

        if(!foundMatch){
            $scope.showMore.clusterFilteredMatrixType.push(addThis);
        } else {
            if($scope.showMore.clusterFilteredMatrixType.length === 0){
                $scope.showMore.clusterFilteredMatrixType = JSON.parse(JSON.stringify($scope.showMore.permaClusterFilteredMatrixType));
            }
        }

        $scope.updateRating();
    }

    $scope.checkFilterState = function() {
        var annotationFilterCount = $scope.showMore.permaClusterFilteredAnnotations.length;
        for(var i=0; i<annotationFilterCount; i++){
            if($("#AX" + i).prop("checked")){
                console.log("Annotation");
                console.log(i);
                return true;
            }
        }

        var matrixFilterCount = $scope.showMore.permaClusterFilteredMatrixType.length;
        for(var i=0; i<matrixFilterCount; i++){
            if($("#MX" + i).prop("checked")){
                console.log("Matrix");
                console.log(i);
                return true;
            }
        }

        var diseaseFilterCount = $scope.showMore.permaClusterFilteredDiseases.length;
        for(var i=0; i<diseaseFilterCount; i++){
            if($("#DX" + i).prop("checked")){
                console.log("Disease");
                console.log(i);
                return true;
            }
        }
    };

    $scope.setDrugGeneFilter = function(addThis) {
        var foundMatch = false;

        if($scope.showMore.drugGeneFilter.length === $scope.showMore.permaDrugGeneFilter.length){
            $scope.showMore.drugGeneFilter = [];

        }
        for(var i=0;i<$scope.showMore.drugGeneFilter.length;i++){
            if(addThis === $scope.showMore.drugGeneFilter[i]){
                $scope.showMore.drugGeneFilter.splice(i, 1);
                foundMatch = true;
                break;
            }
        }

        if(!foundMatch){
            $scope.showMore.drugGeneFilter.push(addThis);
        } else {
            if($scope.showMore.drugGeneFilter.length === 0){
                $scope.showMore.drugGeneFilter = JSON.parse(JSON.stringify($scope.showMore.permaDrugGeneFilter));
            }
        }
    }

    $scope.setAuthorGeneFilter = function(addThis) {
        var foundMatch = false;

        if($scope.checkAuthorFilterState()){
            if($scope.showMore.filterAuthorState === "PAGED"){
                console.log("WAS PAGED.  SWITCHED TO NON-PAGED");
                $scope.peopleGeneTabClickPaged(99);
                $scope.showMore.filterAuthorState = "NOTPAGED";
            }
        } else if($scope.showMore.filterAuthorState === "NOTPAGED"){
            console.log("WAS NON-PAGED.  SWITCHED TO PAGED")
            $scope.peopleGeneTabClickPaged(1);
            $scope.showMore.filterAuthorState = "PAGED";
        }

        if($scope.showMore.authorGeneFilter.length === $scope.showMore.permaAuthorGeneFilter.length){
            $scope.showMore.authorGeneFilter = [];

        }

        for(var i=0;i<$scope.showMore.authorGeneFilter.length;i++){
            if(addThis === $scope.showMore.authorGeneFilter[i]){
                $scope.showMore.authorGeneFilter.splice(i, 1);
                foundMatch = true;
                break;
            }
        }

        if(!foundMatch){
            $scope.showMore.authorGeneFilter.push(addThis);
        } else {
            if($scope.showMore.authorGeneFilter.length === 0){
                $scope.showMore.authorGeneFilter = JSON.parse(JSON.stringify($scope.showMore.permaAuthorGeneFilter));
            }
        }
    }

    $scope.checkAuthorFilterState = function() {
        var authorFilterCount = $scope.showMore.permaAuthorGeneFilter.length;
        for(var i=0; i<authorFilterCount; i++){
            if($("#PX" + i).prop("checked")){
                return true;
            }
        }
    };

    $scope.checkTissueFilterState = function() {
        var tissueFilterCount = $scope.showMore.permaTissuesFilter.length;
        for(var i=0; i<tissueFilterCount; i++){
            if($("#CTX" + i).prop("checked")){
                return true;
            }
        }
    };

    $scope.resultAccumulator = function(){
        $scope.showMore.filteredItemsTotal++;
    }

    $scope.matrixTypeFilterClear = function(domPrefix){
        for(var i=0;i<$scope.showMore.permaClusterFilteredMatrixType.length;i++){
            $("#" + domPrefix + i).prop("checked", false);
        }

        $scope.showMore.clusterFilteredMatrixType = [];
        $scope.showMore.clusterFilteredMatrixType = JSON.parse(JSON.stringify($scope.showMore.permaClusterFilteredMatrixType));

        $scope.updateRating();
    }

    $scope.drugGeneFilterClear = function(domPrefix){
        for(var i=0;i<$scope.showMore.permaDrugGeneFilter.length;i++){
            $("#" + $scope.showMore.permaDrugGeneFilter[i]).prop("checked", false);
        }

        $scope.showMore.drugGeneFilter = [];
        $scope.showMore.drugGeneFilter = JSON.parse(JSON.stringify($scope.showMore.permaDrugGeneFilter));
    }

    $scope.authorGeneFilterClear = function(domPrefix){
        for(var i=0;i<$scope.showMore.permaAuthorGeneFilter.length;i++){
            $("#PX" + i).prop("checked", false);
        }

        $scope.showMore.authorGeneFilter = [];
        $scope.showMore.authorGeneFilter = JSON.parse(JSON.stringify($scope.showMore.permaAuthorGeneFilter));
        $scope.setAuthorGeneFilter();
    }

    $scope.annotationFilterClear = function(domPrefix){
        // Uncheck all the annotation checkboxes
        for(var i=0;i<$scope.showMore.permaClusterFilteredAnnotations.length;i++){
            if($("#" + domPrefix + i) != null){
                $("#" + domPrefix + i).prop("checked", false);
            }
        }

        $scope.showMore.clusterFilteredAnnotations = [];
        $scope.showMore.clusterFilteredAnnotations = JSON.parse(JSON.stringify($scope.showMore.permaClusterFilteredAnnotations));

        $scope.updateRating();
    }

    $scope.diseasesFilterClear = function(domPrefix){
        // Uncheck all the disease checkboxes
        for(var i=0;i<$scope.showMore.permaClusterFilteredDiseases.length;i++){
            if($("#" + domPrefix + i) != null){
                $("#" + domPrefix + i).prop("checked", false);
            }
        }

        $scope.showMore.clusterFilteredDiseases = [];
        $scope.showMore.clusterFilteredDiseases = JSON.parse(JSON.stringify($scope.showMore.permaClusterFilteredDiseases));

        $scope.updateRating();
    }

    $scope.conditionsFilterClear = function(domPrefix){
        // Uncheck all the annotation checkboxes
        for(var i=0;i<$scope.showMore.permaConditionsFilter.length;i++){
            if($("#" + domPrefix + i.toString()) != null){
                $("#" + domPrefix + i.toString()).prop("checked", false);
            }
        }

        $scope.showMore.conditionsFilter = [];
        $scope.showMore.conditionsFilter = JSON.parse(JSON.stringify($scope.showMore.permaConditionsFilter));
    }

    $scope.tissuesFilterClear = function(domPrefix){
        // Uncheck all the annotation checkboxes
        for(var i=0;i<$scope.showMore.permaTissuesFilter.length;i++){
            if($("#" + domPrefix +  + i.toString()) != null){
                $("#" + domPrefix +  + i.toString()).prop("checked", false);
            }
        }

        $scope.showMore.tissuesFilter = [];
        $scope.showMore.tissuesFilter = JSON.parse(JSON.stringify($scope.showMore.permaTissuesFilter));
        $scope.setTissuesFilter();
    }

    //=======================
    // Code borrowed from cytoscapeNav
    //=======================
    $scope.project = {
        "status": "updated",
        "include_neighbors": true,
        "n_connected_neighbors": 20,
        "timestamp": {
            "updated": 1435596974545.36,
            "created": 1435596643611.634
        },
        "do_heat_diffusion": false,
        "state": "finish",
        "n_hottest_neighbors": 20,
        "_id": "55917763f6f407181fa2ec23",
        "networks": {
            "55882d5ff6f407cf1f63f2a3": true,
            "55882d60f6f407cf1f63f62b": true,
            "55882d5ef6f407cf1f63f10a": true,
            "55882d5ff6f407cf1f63f2c8": true,
            "55882d60f6f407cf1f63f520": true,
            "55882d61f6f407cf1f63f6c9": true,
            "55882d61f6f407cf1f63f691": true
        },
        "term_list": [],
        "gene_list": [],
        "genes_list": [],
        "protein_list": [],
        "icd10_list": [],
        "drug_list": [],
        "genome_list": [],
        "disease_list": [],
        "unknown_list": []
    };
    $scope.terms = {
        "all_terms_array": []
    }

    // keep some ui flags here (e.g., genes_as_text, advanced_network)
    // these are not persisted to the server as part of the project
    $scope.show = {};

    // dirty.gene_list is the model for the gene list input box
    $scope.dirty = {
        term_list: ""
    };

    // delete a gene from the gene list and save the project to the server
    $scope.delete_gene = function (term) {
        $scope.project.term_list = _.without($scope.project.term_list, term);
    };

    // clear the entire gene list and save the project to the server
    $scope.delete_gene_list = function () {
        $scope.project.term_list.length = 0;
        $scope.project.genes_list.length = 0;

        $scope.ArrangeTerms();
    };

    $scope.setHoverValue = function (geneId) {
        $scope.hoverValue = geneId;
    };

    $scope.searchBoxFocus = function () {
        if($scope.showFocus) {
            alert();
        }
        $scope.showFocus = false;
    };

    $scope.experiment = function() {
      searchResults.heatmaploading = true;
    };

    $scope.ArrangeTerms = function(){
        $scope.project.genes_list = [];
        $scope.project.gene_list = [];
        $scope.project.protein_list = [];
        $scope.project.icd10_list = [];
        $scope.project.drug_list = [];
        $scope.project.disease_list = [];
        $scope.project.genome_list = [];
        $scope.project.unknown_list = [];
        $scope.terms.all_terms_array = [];

        for (i = 0; i < $scope.project.term_list.length; ++i) {
            if($scope.project.term_list[i].type === 'gene'){
                    $scope.project.genes_list.push($scope.project.term_list[i]);
            } else if($scope.project.term_list[i].type === 'icd10'){
                    $scope.project.icd10_list.push($scope.project.term_list[i]);
            } else if($scope.project.term_list[i].type === 'drug'){
                    $scope.project.drug_list.push($scope.project.term_list[i]);
            } else if($scope.project.term_list[i].type === 'protein'){
                    $scope.project.protein_list.push($scope.project.term_list[i]);
            } else if($scope.project.term_list[i].type === 'disease'){
                    $scope.project.disease_list.push($scope.project.term_list[i]);
            } else if($scope.project.term_list[i].type === 'genome'){
                    $scope.project.genome_list.push($scope.project.term_list[i]);
            } else if($scope.project.term_list[i].type === 'unknown'){
                    $scope.project.term_list[i].termTitle = $scope.project.term_list[i].user;
                    $scope.project.unknown_list.push($scope.project.term_list[i]);
            }
        }
        $scope.terms.all_terms_array.push({"term_type": "gene", "terms": $scope.project.genes_list, "css_class": "btn-green-light"});
        $scope.terms.all_terms_array.push({"term_type": "icd10", "terms": $scope.project.icd10_list, "css_class": "btn-orange-light"});
        $scope.terms.all_terms_array.push({"term_type": "drug", "terms": $scope.project.drug_list, "css_class": "btn-blue-medium"});
        $scope.terms.all_terms_array.push({"term_type": "protein", "terms": $scope.project.protein_list, "css_class": "btn-blue-light"});
        $scope.terms.all_terms_array.push({"term_type": "disease", "terms": $scope.project.disease_list, "css_class": "btn-greenish-medium"});
        $scope.terms.all_terms_array.push({"term_type": "genome", "terms": $scope.project.genome_list, "css_class": "btn-darkorchid3-medium"});
        $scope.terms.all_terms_array.push({"term_type": "unknown", "terms": $scope.project.unknown_list, "css_class": "btn-red-light"});
    };


    /*
    ==============================
    ==============================
     MAIN SEARCH CALL (FROM SEARCH BUTTON)
    ==============================
    ==============================
    */
    $scope.runHttpSearch = function () {
        $scope.showAbout = "INVALID";
        // First check if the user already added terms.
        // If not then the user may have terms in the searchbox ready to process
        $scope.tabWasClicked = [];
        //$location.path('/information');
        if($scope.dirty.term_list.length < 1 && $scope.project.genes_list.length < 1){
            $scope.showTermWarning = false;
            $scope.showSearchWarning = true;
            $scope.showMaxWarning = false;
        } else if($scope.dirty.term_list.length > 0){
            $scope.lastKey = 13;// force the term resolver to process i.e. simulate that the enter key was pressed
            $scope.add_terms(true);
            $scope.showTermWarning = true;
            $scope.showSearchWarning = false;
            $scope.showMaxWarning = false;
        } else if ($scope.project.term_list.length < 1) {
            $scope.lastKey = 13;// force the term resolver to process i.e. simulate that the enter key was pressed
            $scope.add_terms(false);
            $scope.showTermWarning = true;
            $scope.showSearchWarning = false;
            $scope.showMaxWarning = false;
        } else {
            $scope.showTermWarning = false;
            $scope.showSearchWarning = false;
            $scope.showMaxWarning = false;
            $scope.tabWasClicked = [];
            $scope.rangeSlider = {'val': 0.0};
            $scope.searchResultsWithGroups = [];
            searchResults.searchResultsWithGroups = [];

            //===========================================
            // getTabCounts() will call the main search
            // after tab counts are gathered
            // i.e. $scope.pathwaysClick();
            //===========================================
            $scope.getTabCounts();
       }
    };

    $scope.updateSearchTabs = function() {

    };

    $scope.getTabCounts = function() {
        $scope.showMore.clusterFilteredAnnotations = [];
        $scope.showMore.permaClusterFilteredAnnotations = [];
        $scope.showMore.clusterAnnotationGOIds = [];

        $scope.showMore.clusterFilteredMatrixType = [];
        $scope.showMore.permaClusterFilteredMatrixType = [];

        $scope.showMore.clusterFilteredDiseases = [];
        $scope.showMore.permaClusterFilteredDiseases = [];

      var termListArray = [];

      angular.forEach($scope.project.term_list, function (value, key) {
          if(value["type"] === 'gene')
          this.push(value["user"]);
      }, termListArray);

      if(termListArray.length > 500){
          termListArray = termListArray.slice(0,499);
      }

      searchboxValue = termListArray.toString();

      urlstar = $scope.pythonHost + "/api/gettabcounts/" + searchboxValue + "?callback=JSON_CALLBACK";

      $scope.searchResultsWithGroups = [];

      var myrequestStar = HttpServiceJsonp.jsonp(urlstar)
      .success(function (result) {
        $scope.showMore.counts = result;

        if($scope.currentTab === "GENES"){
          $scope.genesTabClick();
        } else if ($scope.currentTab === "PHENOTYPES"){
          $scope.phenotypeClick(1);
        } else if ($scope.currentTab === "PEOPLE_GENE"){
          $scope.peopleGeneTabClick(1);
        } else if ($scope.currentTab === "PATHWAYS"){
          $scope.pathwaysClick(1);
        } else if ($scope.currentTab === "DRUG"){
          $scope.drugTabClick();
        } else {
          $scope.genesTabClick();
        }
      }).finally(function () {
      }).error(function (data, status, headers, config) {
          alert(data + ' - ' + status + ' - ' + headers);
      });
    };

    function searchGenesTab() {
        $scope.showTerms = false;
        $scope.loading = true;
        $scope.resultsPresent = true;
        var searchboxValue = "";
        var cancerTypeValue = "";
        var phenotypeTypeValue = "";
        var termListArray = [];
        var cancerListArray = [];
        var phenotypeListArray = [];

        angular.forEach($scope.project.term_list, function (value, key) {
            if(value["type"] === 'gene')
            this.push(value["user"]);
        }, termListArray);

        angular.forEach($scope.project.term_list, function (value, key) {
            if(value["type"] === 'disease')
            this.push(value["user"]);
        }, cancerListArray);

        angular.forEach($scope.project.icd10_list, function (value, key) {
            if(value["type"] === 'icd10')
            this.push(value["user"]);
        }, phenotypeListArray);

        searchboxValue = termListArray.toString();
        cancerTypeValue = cancerListArray.toString();
        phenotypeTypeValue = phenotypeListArray.toString();

        //$scope.resultsPresent = "true";

        var urlstar = "";
        if($scope.project.genome_list.length > 0 && $scope.project.genome_list[0].user != 'HUMAN') {
            urlstar = $scope.pythonHost + "/nav/elasticsearch/coexpression_network/search/map/" + searchboxValue + "/" + $scope.project.genome_list[0].user + "?callback=JSON_CALLBACK";
            //alert(url);
        } else {
          if(cancerTypeValue.length > 0) {
              urlstar = $scope.pythonHost + "/nav/elasticsearch/star/search/map/" + searchboxValue + "/" + cancerTypeValue + "?callback=JSON_CALLBACK";
          } else {
              urlstar = $scope.pythonHost + "/nav/elasticsearch/star/search/map/" + searchboxValue + "?callback=JSON_CALLBACK";
          }
        }

        $scope.searchResultsWithGroups = [];

        var myrequestStar = HttpServiceJsonp.jsonp(urlstar)
            .success(function (result) {
//                $scope.searchResultsWithGroups = [];
//                searchResults.searchResultsWithGroups = [];

                for (i = 0; i < result.length; ++i) {
                    $scope.searchResultsWithGroups.push(result[i]);
                    searchResults.searchResultsWithGroups.push(result[i]);
                }
                $scope.tabWasClicked.push("GENES");

                $scope.resultsPresent = "true";
                $scope.loading = false;
                //$scope.$apply()
            }).finally(function () {
            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });

    }

    function searchPathwaysTab(pageNumber) {
        $scope.loading = true;
        $scope.showTerms = false;
        $scope.resultsPresent = true;

        //==========================================
        // See services.js for ClusterSearchService
        //==========================================
        ClusterSearchService.getSearchResults($scope.project.term_list, pageNumber)
        .then(
             /* success function */
             function(result) {
                 for (i = 0; i < result.length; ++i) {
                     // We are attaching the ES _id array to the PATHWAYS JSON Object.
                     if(result[i].searchTab === "PATHWAYS"){
                         $scope.clusters.hit_ids = result[i].hit_ids;
                         $scope.clusters.inferred_drug_cluster_ids = result[i].inferred_drug_cluster_ids;
                         $scope.clusters.inferred_drug_cluster_ids_with_disease = result[i].inferred_drug_cluster_ids_with_disease;
                         if(pageNumber != 1){
                             //$scope.showMore.permaClusterFilteredAnnotations = _.union($scope.showMore.permaClusterFilteredAnnotations, result[i].permaClusterFilteredAnnotations)
                             //$scope.showMore.clusterFilteredAnnotations = _.union($scope.showMore.clusterFilteredAnnotations, result[i].clusterFilteredAnnotations)
                             //$scope.showMore.clusterAnnotationGOIds = _.union($scope.showMore.clusterAnnotationGOIds, result[i].clusterAnnotationGOIds)
                             //$scope.showMore.clusterFilteredMatrixType = _.union($scope.showMore.clusterFilteredMatrixType, result[i].clusterFilteredMatrixType)
                             //$scope.showMore.permaClusterFilteredMatrixType = _.union($scope.showMore.permaClusterFilteredMatrixType, result[i].permaClusterFilteredMatrixType)
                             //$scope.showMore.clusterFilteredDiseases = _.union($scope.showMore.clusterFilteredDiseases, result[i].clusterFilteredDiseases)
                             //$scope.showMore.permaClusterFilteredDiseases = _.union($scope.showMore.permaClusterFilteredDiseases, result[i].permaClusterFilteredDiseases)
                         } else {
                             if($scope.showMore.permaClusterFilteredMatrixType.length < 1){
                                 $scope.showMore.clusterFilteredAnnotations = result[i].clusterFilteredAnnotations;
                                 $scope.showMore.permaClusterFilteredAnnotations = result[i].permaClusterFilteredAnnotations;
                                 $scope.showMore.clusterAnnotationGOIds = result[i].clusterAnnotationGOIds;

                                 $scope.showMore.clusterFilteredMatrixType = result[i].clusterFilteredMatrixType;
                                 $scope.showMore.permaClusterFilteredMatrixType = result[i].permaClusterFilteredMatrixType;

                                 $scope.showMore.clusterFilteredDiseases = result[i].clusterFilteredDiseases;
                                 $scope.showMore.permaClusterFilteredDiseases = result[i].permaClusterFilteredDiseases;
                             }
                         }
                     }
                     $scope.searchResultsWithGroups.push(result[i].result);
                     searchResults.searchResultsWithGroups.push(result[i].result);
                 }
                 $scope.resultsPresent = "true";
                 $scope.loading = false;
                 $scope.tabWasClicked.push("PATHWAYS");
                 $scope.updateRating();
             },
             /* error function */
             function(result) {
                 console.log("Failed to get the cluster results, result is " + result);
         });
    }

    function searchPhenotypeTab(pageNumber) {
        $scope.loading = true;
        $scope.showTerms = false;
        $scope.resultsPresent = true;

        ConditionSearchService.getSearchResults($scope.project.term_list, $scope.project.icd10_list, pageNumber)
        .then(
             /* success function */
             function(result) {
                 for (i = 0; i < result.length; ++i) {
                     // We are attaching the ES _id array to the PATHWAYS JSON Object.
                     if(result[i].searchTab === "PHENOTYPES"){
                         var w = angular.element($window);

                         $scope.showMore.resultsPaneHeight =  w.height() - 276;
                         searchResults.searchPaneHeight =  w.height() - 276;


                         if(pageNumber != 1){
                             //$scope.showMore.conditionsFilter = result[i].conditionsFilter;
                             //$scope.showMore.permaConditionsFilter = result[i].permaConditionsFilter;

                             //$scope.showMore.tissuesFilter = result[i].tissuesFilter;
                             //$scope.showMore.permaTissuesFilter = result[i].permaTissuesFilter;
                         } else {
                             $scope.showMore.conditionsFilter = result[i].conditionsFilter;
                             $scope.showMore.permaConditionsFilter = result[i].permaConditionsFilter;

                             $scope.showMore.tissuesFilter = result[i].tissuesFilter;
                             $scope.showMore.permaTissuesFilter = result[i].permaTissuesFilter;
                         }
                     }
                     $scope.searchResultsWithGroups.push(result[i].result);
                     searchResults.searchResultsWithGroups.push(result[i].result);
                 }

                 $scope.resultsPresent = "true";
                 $scope.loading = false;
                $scope.tabWasClicked.push("PHENOTYPES");
             },
             /* error function */
             function(result) {
                 console.log("Failed to get the cluster results, result is " + result);
         });
     };

    function searchGenePeopleTab(pageNumber) {
        $scope.loading = true;
        $scope.showTerms = false;
        $scope.resultsPresent = true;

        AuthorSearchService.getSearchResults($scope.project.term_list, pageNumber)
        .then(
             /* success function */
             function(result) {
                 for (i = 0; i < result.length; ++i) {
                     if(result[i].searchTab === "PEOPLE_GENE"){
                         if(pageNumber != 1){
                             //$scope.showMore.authorGeneFilter = result[i].authorGeneFilter;
                             //$scope.showMore.permaAuthorGeneFilter = result[i].permaAuthorGeneFilter;
                         } else {
                             $scope.showMore.authorGeneFilter = result[i].authorGeneFilter;
                             $scope.showMore.permaAuthorGeneFilter = result[i].permaAuthorGeneFilter;
                         }
                     }
                     $scope.searchResultsWithGroups.push(result[i].result);
                     searchResults.searchResultsWithGroups.push(result[i].result);
                 }

                 $scope.resultsPresent = "true";
                 $scope.loading = false;
                $scope.tabWasClicked.push("PEOPLE_GENE");
                $scope.updateRating();
             },
             /* error function */
             function(result) {
                 console.log("Failed to get the cluster results, result is " + result);
         });
    }

    function searchDrugTab() {
        $scope.loading = true;
        $scope.showTerms = false;
        $scope.resultsPresent = true;

        var disease_to_filter = "";//"Bladder Cancer";
        DrugSearchService.getSearchResults($scope.project.term_list, $scope.clusters.inferred_drug_cluster_ids_with_disease, disease_to_filter)
        .then(
             /* success function */
             function(result) {
                 for (i = 0; i < result.length; ++i) {
                     if(result[i].searchTab === "DRUG"){
                         $scope.showMore.drugGeneFilter = result[i].drugGeneFilter;
                         $scope.showMore.permaDrugGeneFilter = result[i].permaDrugGeneFilter;
                     }
                     $scope.searchResultsWithGroups.push(result[i].result);
                     searchResults.searchResultsWithGroups.push(result[i].result);
                 }

                 $scope.resultsPresent = "true";
                 $scope.loading = false;
                $scope.tabWasClicked.push("DRUG");

                //===============================
                //===============================
                // NOW DO INFERRED DRUG SEARCH
                //===============================
                //===============================
                // clear previous search data
                $scope.drugs.inferred_drugs = [];

                InferredDrugSearchService.getSearchResults($scope.project.term_list, $scope.clusters.inferred_drug_cluster_ids_with_disease, disease_to_filter)
                .then(
                     /* success function */
                     function(result) {
                         $scope.drugs.inferred_drugs = result.result;
                         $scope.drugs.annotate_cluster_info = result.annotate_cluster_info;
                     },
                     /* error function */
                     function(result) {
                         console.log("Failed to get the cluster results, result is " + result);
                 });
             },
             /* error function */
             function(result) {
                 console.log("Failed to get the inferred drug results, result is " + result);
         });
    }

    $scope.getGeneInfo = function(clusterName) {
        var url = $scope.pythonHost + "/nav/restbroker/entrez/" + clusterName + "?callback=JSON_CALLBACK";

        $scope.items = [];
        var myrequest = HttpServiceJsonp.jsonp(url)
            .success(function (result) {
                //alert('updated search');
                //$scope.items = result;
                $scope.items = result['hits'];
            }).finally(function () {

            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });
    };

    $scope.geneNetworkClick = function() {

        var url = $scope.pythonHost + "/nav/elasticsearch/byid/" + searchboxValue + "?callback=JSON_CALLBACK";

        var myrequest = HttpServiceJsonp.jsonp(url)
            .success(function (result) {
                //alert('updated search');
                $scope.networkResult.push(result);
            }).finally(function () {

            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });
    };

    $scope.changeSearchCheckbox = function() {
        $scope.directSearch = !$scope.directSearch;
    };

    $scope.toggle = true;

    $scope.$watch('toggle', function(){
        $scope.toggleText = $scope.toggle ? 'Toggle!' : 'some text';
    });


    function getArrayMembers(arrayToQuery, termsToCheckAgainst) {
        var i = 0;
        returnResults = [];
        for (i = 0; i < termsToCheckAgainst.length; ++i) {
            if (arrayToQuery.indexOf(termsToCheckAgainst[i]) > -1) {
                returnResults.push(termsToCheckAgainst[i]);
            }
        }

        return returnResults;
    }

    $scope.brandIconClick = function() {
        $location.path('/');
        $scope.delete_gene_list();
        //$scope.tabWasClicked.splice(tabIndex, 1);
        $scope.searchResultsWithGroups = [];
        searchResults.searchResultsWithGroups = [];
        $scope.showTerms = true;
        $scope.showFocus = true;
        $scope.pathwayResults = [];
        $scope.currentTab = "PATHWAYS";
        $scope.networkResult = [];
        $scope.networkViewItems = [];
        $scope.directSearch = false;
        $scope.loading = false;
        $scope.pathwaysRespHits = [];
        $scope.tabWasClicked = [];
        $scope.hoverValue = "";
        $scope.rangeSlider = {'val': 0.0};
        $scope.rangeSliderGO = {'val': 100};
        $scope.resultsPresent = false;
        $scope.dirty.term_list = "";
        //var tabIndex = $scope.tabWasClicked.indexOf("GENES");
    };

    $scope.pathwaysClick = function (pageNumber) {
        $scope.currentTab = "PATHWAYS";
        $scope.loading = false;
        $location.path('/pathway-search-results');
        if($scope.tabWasClicked.indexOf("PATHWAYS") < 0){
            searchPathwaysTab(pageNumber);
        }
        $scope.updateRating();
    };

    $scope.updateRating = function(){
        setTimeout(function () {
           $('.rating').rating();
       }, 200);
    }

    $scope.pathwaysClickPaged = function (pageNumber) {
        $scope.currentTab = "PATHWAYS";
        $scope.loading = false;
        $scope.tabWasClicked = [];
//        for(var i=0; i<$scope.tabWasClicked.length; i++){
//            if($scope.tabWasClicked[i] === "PATHWAYS"){
//                $scope.tabWasClicked.splice(i,1);
//            }
//        }

        for(var i=0; i<$scope.searchResultsWithGroups.length; i++){
            if($scope.searchResultsWithGroups[i]["searchTab"] === "PATHWAYS"){
                $scope.searchResultsWithGroups = [];
            }
        }

        for(var i=0; i<searchResults.searchResultsWithGroups.length; i++){
            if(searchResults.searchResultsWithGroups[i]["searchTab"] === "PATHWAYS"){
                searchResults.searchResultsWithGroups = [];//.splice(i,1);
            }
        }

        $location.path('/pathway-search-results');
        searchPathwaysTab(pageNumber);
    };

    $scope.genesTabClick = function () {
        $scope.currentTab = "GENES";
        $scope.loading = false;
        $('#placeHolder').focus();

        $location.path('/gene-search-results');
        if($scope.tabWasClicked.indexOf("GENES") < 0){
            searchGenesTab();
        }

    };

    $scope.peopleGeneTabClick = function (pageNumber) {
        $scope.currentTab = "PEOPLE_GENE";
        $scope.$route.current.activetab = "PEOPLE_GENE"
        $scope.loading = false;
        $location.path('/people-search-results');
        if($scope.tabWasClicked.indexOf("PEOPLE_GENE") < 0){
          searchGenePeopleTab(pageNumber);
        }
        $scope.updateRating();
    };


    $scope.peopleGeneTabClickPaged = function (pageNumber) {
        $scope.currentTab = "PEOPLE_GENE";
        $scope.loading = false;
        //$location.path('/people-search-results');

        $scope.tabWasClicked = [];

        for(var i=0; i<$scope.searchResultsWithGroups.length; i++){
            if($scope.searchResultsWithGroups[i]["searchTab"] === "PEOPLE_GENE"){
                $scope.searchResultsWithGroups = [];
            }
        }

        for(var i=0; i<searchResults.searchResultsWithGroups.length; i++){
            if(searchResults.searchResultsWithGroups[i]["searchTab"] === "PEOPLE_GENE"){
                searchResults.searchResultsWithGroups = [];
            }
        }

        $location.path('/people-search-results');
        searchGenePeopleTab(pageNumber);
    };


    $scope.phenotypeClick = function (pageNumber) {
        $scope.currentTab = "PHENOTYPES";
        $scope.loading = false;
        $location.path('/phenotype-search-results');
        if($scope.tabWasClicked.indexOf("PHENOTYPES") < 0){
            searchPhenotypeTab(pageNumber);
        }
    };

    $scope.phenotypeClickPaged = function (pageNumber) {
        $scope.currentTab = "PHENOTYPES";
        $scope.loading = false;
        //$location.path('/phenotype-search-results');

        $scope.tabWasClicked = [];
//        for(var i=0; i<$scope.tabWasClicked.length; i++){
//            if($scope.tabWasClicked[i] === "PHENOTYPES"){
//                $scope.tabWasClicked.splice(i,1);
//            }
//        }

        for(var i=0; i<$scope.searchResultsWithGroups.length; i++){
            if($scope.searchResultsWithGroups[i]["searchTab"] === "PHENOTYPES"){
                $scope.searchResultsWithGroups = [];
            }
        }

        for(var i=0; i<searchResults.searchResultsWithGroups.length; i++){
            if(searchResults.searchResultsWithGroups[i]["searchTab"] === "PHENOTYPES"){
                searchResults.searchResultsWithGroups = [];
            }
        }

        $location.path('/phenotype-search-results');
        searchPhenotypeTab(pageNumber);
    };

    $scope.drugTabClick = function () {
        $scope.currentTab = "DRUG";
        $scope.loading = false;
        $location.path('/drug-search-results');
        if($scope.tabWasClicked.indexOf("DRUG") < 0){
            searchDrugTab();
        }
    };

    $scope.otherClustersTabClick = function() {
      $scope.currentTab = "OTHER_CLUSTERS";
      $scope.loading = false;
      $location.path('/other-clusters-results');
      if($scope.tabWasClicked.indexOf("PATHWAYS") < 0){
        searchPathwaysTab(1);
      }
    }

    $scope.showSearchControls = function () {
        $scope.showTerms = $scope.showTerms === false ? true : false;
    };

    $scope.openNetworkJson = function(itemToLinkTo) {
        $scope.currentTab = "NETWORKVIEW";
        $scope.currentGene = itemToLinkTo;

        var urlstar = $scope.pythonHost + "/nav/elasticsearch/single/star/search/map/" + itemToLinkTo + "?callback=JSON_CALLBACK";
        var myrequestStar = HttpServiceJsonp.jsonp(urlstar)
            .success(function (result) {

                $scope.networkViewItems = result.hits.hits[0]._source.node_list;//['hits']['hits']['fields'];

            }).finally(function () {
            }).error(function (data, status, headers, config) {
                alert(data + ' - ' + status + ' - ' + headers);
            });
        //alert(itemToLinkTo);
    };

    // this method is called on any activity in the gene list input box
    // force is true when the user moves focus away from the input box and causes us to process the entire word
    // otherwise, the user could be in the middle of typing the last word and we wait for them to finish
    $scope.add_terms = function (force) {
        //$location.path('/gene-search-results');
        if (areTermsReadyToProcess(force)) {
          $scope.showSearchWarning = false;

            var words = angular.copy($scope.dirty.term_list);
            //var words = _.words($scope.dirty.term_list, /[\w0-9\-_]+/g);
            if(words.indexOf("JSON_CALLBACK") > -1){
                words = words.replace(/JSON_CALLBACK/g, "");
            }
            words = words.replace(/\//g, "");
            words = words.replace(/\?/g, "");
            words = words.replace(/^\s+|\s+$/g,''); //Trim trailing and leading spaces
            words = words.replace(/ +/g, " "); // Trim multiple spaces
            words = words.replace(/(?:\r\n|\r|\n|\s)/g, ',');
            words = words.replace(/^[,\s]+|[,\s]+$/g, '').replace(/,[,\s]*,/g, ',');

            if((words.slice(-1) === ',') || (words.slice(-1) === ' ')) {
                words = words.substring(0, words.length - 1);
            }
            $timeout(function() {
              $scope.saveSearchState(words);
          }, 100);


            wordsArray = words.split(',');
            //alert(wordsArray.length);

            //=======================================
            // Chunk the term resolution
            //=======================================
            var batchSize = Math.trunc(wordsArray.length / 50);
            if(wordsArray.length % 50 === 0) {
                batchSize -= 1;
            }
            console.log(batchSize);
            for(i=0;i<=batchSize;i++){
                words1Array = wordsArray.slice(i*50, (i+1)*50);
                words1 = words1Array.join();
                if(batchSize === i) {
                  $scope.add_terms_http_call(words1,true);
                } else {
                  $scope.add_terms_http_call(words1,false);
                }
            }

        }
    };

    $scope.add_terms_http_call = function(words, lastBatch){
        var url = $scope.pythonHost + "/nav/terms/lookup/" + words + "?callback=JSON_CALLBACK";

        //alert(words.length);

        $scope.dirty.term_list = "";

        //console.log("Dirty list: " + $scope.dirty.term_list);
        //console.log("Gene list: " + $scope.project.genes_list);

        if(words.length > 0){
            var myrequest = HttpServiceJsonp.jsonp(url)
            .success(function (result) {
                //$scope.resultsPresent = "true";

                $scope.testingJson = result.termClassification;

                var termResults = result.termClassification;
                var foundDup = false;

                if (Object.prototype.toString.call(termResults) === '[object Array]') {

                    termResults.forEach(function (entry) {
                      foundDup = false;
                        //alert(entry["probabilitiesMap"]["gene"]);
                        for(var i=0; i< $scope.project.term_list.length; i++){
                          if($scope.project.term_list[i]["user"] === entry["termId"]){
                            //alert(entry["termId"]);
                            foundDup = true;
                          }
                        }

                        if(!foundDup){
                          if (entry["probabilitiesMap"]["gene"] > 0.2) {
                              var term = {'user': entry["termId"], 'termTitle': entry["termTitle"], "type": "gene"};
                              //$scope.project.gene_list.push(term);

                              if(term["user"].indexOf("HSA-") > -1){
                                term["user"] = term["user"].toLowerCase();
                                term["termTitle"] = term["termTitle"].toLowerCase();
                              }
                              $scope.project.gene_list.unshift(term);
                              $scope.project.term_list.unshift(term);
                          }

                          if (entry["probabilitiesMap"]["icd10"] > 0.2) {
                              var term = {'user': entry["termId"], 'termTitle': entry["termTitle"], "type": "icd10"};
                              $scope.project.gene_list.push(term);
                              $scope.project.term_list.unshift(term);
                          }

                          if (entry["probabilitiesMap"]["drug"] > 0.2) {
                              var term = {'user': entry["termId"], 'termTitle': entry["termTitle"], "type": "drug"};
                              $scope.project.gene_list.push(term);
                              $scope.project.term_list.unshift(term);
                          }

                          if (entry["probabilitiesMap"]["disease"] > 0.2) {
                              var term = {'user': entry["termId"], 'termTitle': entry["termTitle"], "type": "disease"};
                              $scope.project.gene_list.push(term);
                              $scope.project.term_list.unshift(term);
                          }

                          if (entry["probabilitiesMap"]["genome"] > 0.2) {
                              var term = {'user': entry["termId"], 'termTitle': entry["termTitle"], "type": "genome"};
                              $scope.project.gene_list.push(term);
                              $scope.project.term_list.unshift(term);
                          }

                          if (entry["status"] === 'unknown') {
                              var term = {'user': entry["termId"], 'termTitle': entry["termTitle"], "type": "unknown"};
                              $scope.project.gene_list.push(term);
                              $scope.project.term_list.unshift(term);
                          }
                        }
                    });

                } else { //NOT AN ARRAY
                  foundDup = false;
                    //alert(entry["probabilitiesMap"]["gene"]);
                    for(var i=0; i< $scope.project.term_list.length; i++){
                      if($scope.project.term_list[i]["user"] === entry["termId"]){
                        //alert(entry["termId"]);
                        foundDup = true;
                      }
                    }

                    if(!foundDup){
                      if (termResults["probabilitiesMap"]["gene"] > 0.2) {
                          var term = {'user': termResults["termId"], 'termTitle': termResults["termTitle"], "type": "gene"};
                          //$scope.project.gene_list.push(term);
                          if(term["user"].indexOf("HSA-") > -1){
                            term["user"] = term["user"].toLowerCase();
                            term["termTitle"] = term["termTitle"].toLowerCase();
                          }
                          $scope.project.gene_list.unshift(term);
                          $scope.project.term_list.unshift(term);
                      }
                      if (termResults["probabilitiesMap"]["icd10"] > 0.2) {
                          var term = {'user': termResults["termId"], 'termTitle': termResults["termTitle"], "type": "icd10"};
                          $scope.project.gene_list.push(term);
                          $scope.project.term_list.unshift(term);
                      }
                      if (termResults["probabilitiesMap"]["drug"] > 0.2) {
                          var term = {'user': termResults["termId"], 'termTitle': termResults["termTitle"], "type": "drug"};
                          $scope.project.gene_list.push(term);
                          $scope.project.term_list.unshift(term);
                      }

                      if (termResults["probabilitiesMap"]["disease"] > 0.2) {
                          var term = {'user': termResults["termId"], 'termTitle': termResults["termTitle"], "type": "disease"};
                          $scope.project.gene_list.push(term);
                          $scope.project.term_list.unshift(term);
                      }
                      if (termResults["probabilitiesMap"]["genome"] > 0.2) {
                          var term = {'user': termResults["termId"], 'termTitle': termResults["termTitle"], "type": "genome"};
                          $scope.project.gene_list.push(term);
                          $scope.project.term_list.unshift(term);
                      }
                      if (termResults["status"] === 'unknown') {
                          var term = {'user': termResults["termId"], 'termTitle': termResults["termTitle"], "type": "unknown"};
                          $scope.project.gene_list.push(term);
                          $scope.project.term_list.unshift(term);
                      }
                    }
                }

                $scope.ArrangeTerms();

                $scope.bridgeService.info.search_terms = angular.copy($scope.project.term_list);

                if(lastBatch){
                    $timeout(function() {
                        $scope.runHttpSearch();
                    }, 500);
                }
            }).finally(function () {
                //alert();
            }).error(function (data, status, headers, config) {
                //alert("term complete");
                alert(data + ' - ' + status + ' - ' + headers);
            });

        } else {
            if(lastBatch){
                $timeout(function() {
                    $scope.runHttpSearch();
                }, 200);
            }
        }
    };

    function areTermsReadyToProcess(force) {
        if($scope.previousLastKey === 40 || $scope.previousLastKey === 38){
          return false;
        } else if($scope.lastKey != 13){
            return false;
        }



        //var wordsChecker = _.words($scope.dirty.term_list, /[\w0-9\-_]+/g);
        var wordsChecker = _.words($scope.dirty.term_list, /[\w0-9\-_]+/g);
        var isReady = false;

        // if there is more than one word, we assume that the user cut and pasted into the input box
        // in this case, we treat the last word as complete rather than waiting for the user to continue typing
        // TODO decide if this behavior is more annoying or useful
        force = force || wordsChecker.length > 1;

        // we might leave the last word alone if the user is still typing
        var last = wordsChecker.slice(-1)[0];
        if (last === undefined) {
//            alert(force);
            // no word in progress, so clear the input box
            $scope.dirty.term_list = "";
            if($scope.lastKey === 13 && !force){
                $scope.runHttpSearch();
                  //              alert('enter was last');
            }
            return false;
        } else {
            if (!force && $scope.dirty.term_list.slice(-last.length) === last) {
                // the final word is still being typed, so leave it in the input box and process the rest (if any)
                wordsChecker = _.initial(wordsChecker);
                $scope.dirty.term_list = last;
            } else {
                // process all words, so clear the input box
                $scope.dirty.gene_list = "";
            }
            //alert("words.length " + words.length);
            if (wordsChecker.length > 0) {
                isReady = true;
            }

        }
        return isReady;
    }

    $scope.logKey = function(keyId) {
        $scope.previousLastKey = $scope.lastKey;
        $scope.lastKey = keyId;
        //LookHere
    };

    $scope.logEscKey = function(keyId) {
        if(keyId === 27){
            $scope.bridgeService.info.showVisDefault = false;
            $scope.bridgeService.info.showVisWithOverlap = false;
            $scope.bridgeService.info.showEnrichment = false;
            $scope.bridgeService.info.showMatrix = false;
            $scope.bridgeService.info.showHeatDiffusion = false;
            bridgeService.info.heatOverlapNodes = [];
        }
    };

    $scope.changeType = function (changeThisTerm, changeToThisType) {
        //alert(changeThisTerm.user); //it.user}} - {{it.type
        var found = $filter('filter')($scope.project.term_list, function (d) {
            return d.user === changeThisTerm.user;
        });

        if (found.length > 1) {
            var i = 0;
            for (i = 0; i < found.length; i++) {
                if (found[i].type === changeThisTerm.type) {
                    if (changeToThisType === "delete") {
                        $scope.project.term_list = _.without($scope.project.term_list, found[i]);
                    } else {
                        found[i].type = changeToThisType;
                    }
                }
            }
        } else {
            if (changeToThisType === "delete") {
                $scope.project.term_list = _.without($scope.project.term_list, found[0]);
            } else {
                if(found[0].termTitle === "none"){
                    found[0].termTitle = found[0].user;
                }
                found[0].type = changeToThisType;
            }
        }
		$scope.ArrangeTerms();

        //$scope.$broadcast = '$locationChangeSuccess';
    };

    $scope.setIFrameContent = function(setThisParm) {
        if($scope.currentTab == "PEOPLE_GENE") {
          $('#myModalLabel').html("People");
        }
        $('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
          $(this).find('iframe').attr('src',setThisParm);
          $('#myModalLabel').html($scope.webServerHost + "/partials/" + setThisParm);
        });
    };

    $scope.setGeneInfoModal = function(setThisParm) {
        var w = angular.element($window);
        var useThisHeight = w.height() - 108;
        var useThisWidth = w.width() - 18;

      $('#myModalBody').html("<iframe src='about:blank' width='" + useThisWidth + "' height='" + useThisHeight + "' style='height: 98%; width: 100%;' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
      $('#myModal').css('height', $scope.info.windowHeight-20);
      historySize = window.history.length;
      var termIdTitle = GetQueryStringParams(setThisParm, "termId");
      var itemClicked = GetQueryStringParams(setThisParm, "currentTab");

      if(termIdTitle.length > 35) {
        termIdTitle = termIdTitle.substring(0, 34) + "...";
      }
      var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";

      $('#myModalLabel').html(modalTitle);

        $timeout(function() {
          $("#myModalBody").find('iframe').attr('src',"partials/" + setThisParm);
        }, 200);
    };

    $scope.resizeDirective = function() {
        $timeout(function() {
            rescale();
        }, 200);
    }

    $scope.selected = undefined;
    $scope.states = [];

    $scope.clearIFrameContent = function() {
    };

    // submit a job request via REST interface
    // this takes a snapshot of the current project, submits the job to the server, and then polls for status updates
    $scope.submit_job = function () {
        $scope.submit_job_request = HttpService.put('/api/nav/project/' + $scope.project._id + '/submit')
            .success($scope.get_jobs);
    };

    function GetQueryStringParams(sPageURL, sParam)
    {
        var queryTerms = sPageURL.split('?');
        if(queryTerms.length > 1){
          var sURLVariables = queryTerms[1].split('&');
          for (var i = 0; i < sURLVariables.length; i++)
          {
              var sParameterName = sURLVariables[i].split('=');
              if (sParameterName[0] == sParam)
              {
                  return sParameterName[1];
              }
          }
        } else {
          return ""
        }
    }
});

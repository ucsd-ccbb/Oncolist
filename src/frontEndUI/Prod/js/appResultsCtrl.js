var app = angular.module('myApp'); //ui-bootstrap


app.controller( "resultsController",function($scope, $window, HttpServiceJsonp, searchResults, $routeParams, $timeout){
    $scope.searchResultsWithGroups = searchResults.searchResultsWithGroups;
    $scope.searchResults = searchResults;
    $scope.sortType = "topOverlap";

    $scope.terms_list = "";
    if($scope.searchResultsWithGroups.length > 0){
      for(var i=0; i< $scope.searchResultsWithGroups[0].geneSuperList.length; i++){
        $scope.terms_list += $scope.searchResultsWithGroups[0].geneSuperList[i]["queryTerm"] + ",";
      }

      $scope.terms_list = $scope.terms_list.substring(0, $scope.terms_list.length - 1);
    }
    $scope.plotlyData = {
      "passThisDataAlong": {},
      "passThisLayoutAlong": {},
      "heatmapFullHeight": 1000,
      "heatmapFullWidth": 1000
    };

    $scope.info = {
      esIdInputVal: "",
      showVis: false,
      selectedConditionData: {"condition_item": {"cosmic_id": "1234", "gene": "ABC"}},
      selectedConditionTissue: "Tissue",
      selectedConditionDisease: "Disease"
    };

    $scope.showgraphSidebar = false;
    $scope.toggleSidebar = function() {
        $scope.showgraphSidebar = !$scope.showgraphSidebar;
    }

    $scope.searchAnalysis = {
        "results": ""
    };

    $scope.showMoreResults = {
      'genes': false,
      'pathways': false,
      'drugs': false,
      'phenotypes': false,
      'proteins': false,
      'diseases': false,
      'genomes': false,
      'unknowns': false,
      'smallScreen': true,
      'drug_limit_direct_hits': 5,
      'pagingClusterPage': 1,
      'pagingConditionPage': 1,
      'pagingAuthorPage': 1
    };

    $scope.$watch(function(){return searchResults.searchResultsWithGroups}, function(NewValue, OldValue){
        //console.log(NewValue + ' ' + OldValue);
        $scope.searchResultsWithGroups = NewValue;

        $scope.terms_list = "";
        if($scope.searchResultsWithGroups.length > 0){
          for(var i=0; i< $scope.searchResultsWithGroups[0].geneSuperList.length; i++){
            $scope.terms_list += $scope.searchResultsWithGroups[0].geneSuperList[i]["queryTerm"] + ",";
          }

          $scope.terms_list = $scope.terms_list.substring(0, $scope.terms_list.length - 1);
        }

    },true);

    $scope.pythonHost = python_host_global; //use variable from env.js
    $scope.showPeople = false;

    $scope.spinner = {
      'heatmaploading': false,
      'tmp1': true
    };

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

    var searchResultsCallback = function(){
      $scope.searchResultsWithGroups = searchResults.searchResultsWithGroups;
    }

    $scope.hydratePeople = function(term, emphasizeInfoArray){
      $scope.showPeople = !$scope.showPeople;
      //alert(term);
      if(showPeople){
        var url = $scope.pythonHost + "/api/get/people/genecenter/lazysearch/hydrate/" + term + "?callback=JSON_CALLBACK";
        var myrequest = HttpServiceJsonp.jsonp(url)
        .success(function (result) {
          emphasizeInfoArray = result;
          alert(emphasizeInfoArray);
        }).finally(function () {
        }).error(function (data, status, headers, config) {
                      alert(data + ' - ' + status + ' - ' + headers);
        });
      }
    };

    $scope.getPlotlyGraph = function(){
        return {
            data: $scope.plotlyData.passThisDataAlong,
            layout: $scope.passThisLayoutAlong
        };
    };

    $scope.resizeDirective = function() {
        $timeout(function() {
            rescale();
        }, 200);
    }

    $scope.resizeHeatMap = function() {
      var heatMapDiv = $('#heatmap').width($scope.plotlyData.heatmapFullWidth).height($scope.plotlyData.heatmapFullHeight);

      var update = {
        width: $scope.plotlyData.heatmapFullWidth,  // or any new width
        height: $scope.plotlyData.heatmapFullHeight  // " "
      };

      Plotly.relayout('heatmap', update);
    }

    $scope.heatmapTabClick3 = function(esId, heatmap_title) { //AVCLoiXeOvM8reJwt0oQ
      $('#heatmapIsLoading').html('<span class="fa fa-spinner fa-2x fa-pulse"></span>');
      var url = $scope.pythonHost + "/nav/elasticsearch/getheatmap3/" + esId + "?callback=JSON_CALLBACK";
      $('#heatmap').css( "display", "none" );
      var myrequest = HttpServiceJsonp.jsonp(url)
           .success(function (result) {
             $('#heatmapIsLoading').html('<h4>Cluster - ' + heatmap_title + '</h4>');

             width = 2 * 830;
             height = 2 * 833;
             if(height > 800){
               height = 570;
             }

             $scope.plotlyData.heatmapFullHeight = 22 * result.yValues.length + 180;

             if(width > 800){
               width = 570;
             }

             $scope.plotlyData.heatmapFullWidth = 22 * result.xValues.length + 100;

             $('#heatmap').width(width).height(height);

             var xValues = result.xValues;

             var yValues = result.yValues;

             var zValues = result.zValues;

             var colorscaleValue = [
               [0, '#ee4035'],
               [1, '#0392cf']
             ];

             var data = [{
               x: xValues,
               y: yValues,
               z: zValues,
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

             $('#heatmap').css( "display", "block" );
           }).finally(function () {
      }).error(function (data, status, headers, config) {
                    alert(data + ' - ' + status + ' - ' + headers);
      });
    };

    $scope.getNetworkEnrichment = function(esId){
        var url = $scope.pythonHost + "/api/elasticsearch/getclusterenrichmentbyid/" + esId + "?callback=JSON_CALLBACK";
        var myrequest = HttpServiceJsonp.jsonp(url)
             .success(function (result) {
                  $scope.modalData = result;
             }).finally(function () {
        }).error(function (data, status, headers, config) {
            alert(data + ' - ' + status + ' - ' + headers);
        });
    };

    $scope.setModalData = function (setThisData) {
        $scope.modalData = setThisData;
    };

    $scope.getSearchAnalysis = function(){
        var url = $scope.pythonHost + "/search/clusters/GATA1,GATA2,GATA3?callback=JSON_CALLBACK";
        var myrequest = HttpServiceJsonp.jsonp(url)
             .success(function (result) {
                  $scope.searchAnalysis.results = result;
             }).finally(function () {
        }).error(function (data, status, headers, config) {
            alert(data + ' - ' + status + ' - ' + headers);
        });
    };

    $scope.renderCytoscape = function(geneTitle){
        cytoObj = {
                layout: { name: 'cose',  animate: true, randomize: true, numIter: 100, initialTemp: 50, animationDuration: 50},
                style: [{ selector: 'node', style: { 'content': 'data(shortName)', 'text-wrap': 'wrap','width': 'mapData(score, 5, 70, 20, 50)', 'height': 'mapData(score, 5, 70, 20, 50)', 'text-valign': 'center','color': 'white',
                        'text-outline-width': 2, 'background-color': 'mapData(score, 5, 20, #034261, #79cbf2)', 'text-outline-color': 'mapData(score, 5, 20, #034261, #79cbf2)', 'font-size': 6} }
                        ],
                elements: [],
                container: document.getElementById('cy')
        };

        var cytoObj2 = {
                elements: [
                        {"data": {"shortName": "LOC100188947", "id": "LOC100188947;HECTD2:10-93169999", "score": 0.5}, "group": "nodes"},
                        {"data": {"shortName": "MAEA", "id": "MAEA:4-1309340", "score": 0.4}, "group": "nodes"}
                        ]
        };

        var geneId = $routeParams.id;

         //var url2 = $scope.pythonHost + "/nav/elasticsearch/cytoscape/star/" + geneTitle.replace(':','') + "?callback=JSON_CALLBACK";
         var url2 = $scope.pythonHost + "/nav/elasticsearch/cytoscape/star/" + geneId.replace(':','') + "?callback=JSON_CALLBACK";
          var myrequest = HttpServiceJsonp.jsonp(url2)
               .success(function (result) {
                    cytoObj['elements']  = result;

                    cy = cytoscape(cytoObj);
                    var options = {};

                    cy.makeLayout(options);
                    cy.panningEnabled(true);
               }).finally(function () {
          }).error(function (data, status, headers, config) {
                        alert(data + ' - ' + status + ' - ' + headers);
          });
      };

      $scope.setConditionInfoModal = function(){
          var w = angular.element($window);
          var useThisHeight = w.height() - 75;

        $('#conditionsModalBody').height(useThisHeight);
    };

    $scope.setIFrameContent = function(setThisParm) {
        var w = angular.element($window);
        var useThisHeight = w.height() - 68;
        var useThisWidth = w.width() - 18;

      $('#myModalBody').html("<iframe src='about:blank' width='" + useThisWidth + "' height='" + useThisHeight + "' style='height: 100%; width: 100%;' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
      $('#myModal').css('height', $scope.info.windowHeight);
      historySize = window.history.length;
      var termIdTitle = GetQueryStringParams(setThisParm, "termId");
      var itemClicked = GetQueryStringParams(setThisParm, "currentTab");
      var title = GetQueryStringParams(setThisParm, "title");

      if(termIdTitle.length > 35) {
        termIdTitle = termIdTitle.substring(0, 34) + "...";
      }
      var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";

      if($scope.currentTab === "PEOPLE_GENE") {
        modalTitle = modalTitle + "<small><a href='https://www.google.com/webhp?hl=en#safe=off&hl=en&q=" + termIdTitle + "' target='_blank'>Author information</a> (opens in a new window)</small>";
        }
        else if(itemClicked === "CONDITION"){
            modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + title + " &nbsp;&nbsp";
        } else if(itemClicked != "PEOPLE_GENE"){
            modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";
        }


      $('#myModalLabel').html(modalTitle);

        //$('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
        //  $(this).find('iframe').attr('src',"/partials/" + setThisParm);
        //});

        $timeout(function() {
          $("#myModalBody").find('iframe').attr('src',"partials/" + setThisParm);
          //var myTemp = $("#myClusterModalBody").find('iframe').attr('src');
        }, 200);

    };

    $scope.setExternalIFrameContent = function(setThisParm) {
      $('#myModalBody').html("<iframe src='about:blank' width='100%' height='600' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
      historySize = window.history.length;
      var termIdTitle = GetQueryStringParams(setThisParm, "termId");

      if(termIdTitle.length > 35) {
        termIdTitle = termIdTitle.substring(0, 34) + "...";
      }
      var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";

      if($scope.currentTab == "PEOPLE_GENE") {
        modalTitle = modalTitle + "<small><a href='https://www.google.com/webhp?hl=en#safe=off&hl=en&q=" + termIdTitle + "' target='_blank'>Author information</a> (opens in a new window)</small>";
      }

      $('#myModalLabel').html(modalTitle);

        //$('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
        //  $(this).find('iframe').attr('src',"/partials/" + setThisParm);
        //});

        $timeout(function() {
          $("#myModalBody").find('iframe').attr('src',setThisParm);
          //var myTemp = $("#myClusterModalBody").find('iframe').attr('src');
        }, 200);

    };

    $scope.setClusterIFrameContent = function(setThisParm, esId, overlapGenes) {
        var w = angular.element($window);
        var useThisHeight = w.height() - 68;
        var useThisWidth = w.width() - 18;

      $('#myClusterModalBody').html("<iframe src='about:blank' width='" + useThisWidth + "' height='" + useThisHeight + "' style='overflow-x: hidden; overflow-y: hidden;' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
      $('#myClusterModal').css('height', $scope.info.windowHeight);
      historySize = window.history.length;
      var termIdTitle = GetQueryStringParams(setThisParm, "termId");
      //var overlapGenes = GetQueryStringParams(setThisParm, "geneList");
      //$('#esIdInput').val(esId);

      searchResults.info.esIdInput = esId;
      searchResults.info.overlap = overlapGenes;
      searchResults.info.winHeight = useThisHeight;

      //$scope.info.esIdInputVal = esId;

      console.log("searchResultsController");

      if(termIdTitle.length > 35) {
        termIdTitle = termIdTitle.substring(0, 34) + "...";
      }
      var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;<span style='white-space: nowrap;'>" + termIdTitle + "</span> &nbsp;&nbsp";

      $('#modalTitle').html(modalTitle);

//      $('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
//        $(this).find('iframe').attr('src',setThisParm);
//      });
      $timeout(function() {
        $("#myClusterModalBody").find('iframe').attr('src',"partials/" + setThisParm);
        //var myTemp = $("#myClusterModalBody").find('iframe').attr('src');
      }, 200);

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

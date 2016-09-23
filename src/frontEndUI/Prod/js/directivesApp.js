var app = angular.module('myApp'); //ui-bootstrap

var useLocalHost = false;

var cy;

var historySize = 0;

/*
==========================================
==========================================
        GENERIC
        SEARCH RESULTS DIRECTIVE
==========================================
==========================================
*/
app.directive('moreLessGenes', function () {
    function link(scope, el, attrs) {
       scope.setIFrameContent = function(setThisParm) {
         $('#myModalBody').html("<iframe src='about:blank' width='100%' height='600' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
         historySize = window.history.length;
         var termIdTitle = GetQueryStringParams(setThisParm, "termId");
         if(termIdTitle.length > 35) {
           termIdTitle = termIdTitle.substring(0, 34) + "...";
         }
         var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";

         if(scope.currentTab == "PEOPLE_GENE") {
           modalTitle = modalTitle + "<small><a href='https://www.google.com/webhp?hl=en#safe=off&hl=en&q=" + termIdTitle + "' target='_blank'>Author information</a> (opens in a new window)</small>";
         }

         $('#myModalLabel').html(modalTitle);

           $('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
             $(this).find('iframe').attr('src',setThisParm);
           });
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

       scope.hitsInternal = JSON.parse(attrs.hitsDirective);
       scope.showMore = {
         'local': false
       };

    }

    return {
      scope: {},
      restrict: "EA",
      template: "<div>" +
                "<div ng-repeat='enphasizeThis in hitsInternal | orderBy:\"weight\":true' class='btn-group' ng-hide='$index > 3 && !showMore.local'>" +
                "  <button class='btn btn-link text-muted-dark' style='padding: 0px 5px 0px 0px;' ng-if='$index < 1 && hitsInternal.length > 4' ng-click='showMore.local = !showMore.local'>" +
                "      <span ng-if='showMore.local'><span class='fa fa-minus-square-o fa-lg'></span></span>" +
                "      <span ng-if='!showMore.local'><span class='fa fa-plus-square-o fa-lg'></span></span>" +
                "  </button>" +
                "  <button ng-click='setIFrameContent(\"http://geneli.st:8181/Prototype2/partials/information.html?termId=\" + enphasizeThis.name + \"&currentTab=GENE&snps=\")'" +
                "    data-toggle='modal' data-target='#myModal'" +
                "    class='btn btn-default btn-xs' type='button'>{{enphasizeThis.name}} <br />({{enphasizeThis.weight}})</button>" +
                "{{hitsInternal.diseaseType}}" +
                "</div><img src='images/buttonFade.png' ng-if='hitsInternal.length > 4 && !showMore.local'></img>",
      link: link
    };
});

/*
==========================================
==========================================
        CONDITIONS
        SEARCH RESULTS DIRECTIVE
==========================================
==========================================
*/
app.directive('moreLessConditions', function ($timeout) {
    function link(scope, el, attrs) {
       scope.setIFrameContent = function(setThisParm) {
         $('#myModalBody').html("<iframe src='about:blank' width='100%' height='600' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
         historySize = window.history.length;
         var termIdTitle = GetQueryStringParams(setThisParm, "termId");
         if(termIdTitle.length > 35) {
           termIdTitle = termIdTitle.substring(0, 34) + "...";
         }
         var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";

         if(scope.currentTab == "PEOPLE_GENE") {
           modalTitle = modalTitle + "<small><a href='https://www.google.com/webhp?hl=en#safe=off&hl=en&q=" + termIdTitle + "' target='_blank'>Author information</a> (opens in a new window)</small>";
         }

         $('#myModalLabel').html(modalTitle);

           //$('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
          //   $(this).find('iframe').attr('src',setThisParm);
           //});

           $timeout(function() {
             $("#myModalBody").find('iframe').attr('src',"partials/" + setThisParm);
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

       scope.hitsInternal = JSON.parse(attrs.hitsDirective);
       scope.showMore = {
         'local': false
       };

    }

    return {
      scope: {},
      restrict: "EA",
      template: "<div  style='margin-left: 10px;'> " +
                //"{{hitsInternal}}" +
                "  <div ng-repeat='enphasizeThis in hitsInternal | orderBy:\"phenotype_name\"' style='margin-right: 0px;' class='btn-group' ng-hide='$index > 3 && !showMore.local'>" +
                "    <button class='btn btn-link text-muted-dark' style='padding: 0px 5px 0px 0px;' ng-if='$index < 1 && hitsInternal.length > 4' ng-click='showMore.local = !showMore.local'>" +
                "        <span ng-if='showMore.local'><span class='fa fa-minus-square-o fa-lg'></span></span>" +
                "        <span ng-if='!showMore.local'><span class='fa fa-plus-square-o fa-lg'></span></span>" +
                "    </button>" +
                "    <button ng-click='setIFrameContent(\"information.html?ElasticId=\" + enphasizeThis.hit_id + \"&termId=\" + enphasizeThis.phenotype_name + \"&currentTab=PHENOTYPE&snps=\")'" +
                "      data-toggle='modal' data-target='#myModal'" +
                "      class='btn btn-primary btn-xs' style='margin-left: 3px; margin-bottom: 3px;' type='button'>{{enphasizeThis.phenotype_name}}</button>" +
                "  </div>" +
                "  <img src='images/buttonFadeSmallBlue.png' style='margin-left: -1px; margin-bottom: 3px;' ng-if='hitsInternal.length > 4 && !showMore.local'></img>" +
                "</div>",
      link: link
    };
});

/*
==========================================
==========================================
        DRUGS
        SEARCH RESULTS DIRECTIVE
==========================================
==========================================
*/
app.directive('moreLessDrugs', function () {
    function link(scope, el, attrs) {
       scope.setIFrameContent = function(setThisParm) {
         $('#myModalBody').html("<iframe src='about:blank' width='100%' height='600' frameborder='0' allowtransparency='true' id='myIFrame' name='contentframe'></iframe>");
         historySize = window.history.length;
         var termIdTitle = GetQueryStringParams(setThisParm, "termId");
         if(termIdTitle.length > 35) {
           termIdTitle = termIdTitle.substring(0, 34) + "...";
         }
         var modalTitle = "&nbsp;&nbsp;&nbsp;&nbsp;" + termIdTitle + " &nbsp;&nbsp";

         if(scope.currentTab == "PEOPLE_GENE") {
           modalTitle = modalTitle + "<small><a href='https://www.google.com/webhp?hl=en#safe=off&hl=en&q=" + termIdTitle + "' target='_blank'>Author information</a> (opens in a new window)</small>";
         }

         $('#myModalLabel').html(modalTitle);

           $('.modal').on('shown.bs.modal',function(){      //correct here use 'shown.bs.modal' event which comes in bootstrap3
             $(this).find('iframe').attr('src',setThisParm);
           });
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

       scope.hitsInternal = JSON.parse(attrs.hitsDirective);
       scope.showMore = {
         'local': false
       };
    }

    return {
      scope: {},
      restrict: "EA",
      template:

                "<p ng-repeat='grouped_title in hitsInternal' style='margin-left: 10px;' ng-hide='$index > 2 && !showMore.local'>" +
                "  <button class='btn btn-link text-muted-dark' style='padding: 0px 5px 0px 0px; margin-left: -10px;' ng-if='$index < 1 && hitsInternal.length > 3' ng-click='showMore.local = !showMore.local'>" +
                          "      <span ng-if='showMore.local'><span class='fa fa-minus-square-o fa-lg'></span></span>" +
                          "      <span ng-if='!showMore.local'><span class='fa fa-plus-square-o fa-lg'></span></span>" +
                          "  </button>" +
                "  <a href='#/drug-search-results' data-toggle='modal' data-target='#myModal' ng-click='setIFrameContent(\"http://geneli.st:8181/Prototype2/partials/information.html?termId=\" + grouped_title.drug_name + \"&dbId=\" + grouped_title.drugbank_id + \"&currentTab=DRUG&snps=\")'>" +
                "    {{grouped_title.drug_name}}" +
                "  </a>" +
                "</p>",
      link: link
    };
});

/*
==========================================
==========================================
        DRUGS
        HEAT PROP EVIDENCE GRAPH
==========================================
==========================================
*/
app.directive('heatevidence', function () {
    function link(scope, el, attrs) {
        scope.info = {
          "doneRendering": false
        };

       var vizOptions = {
           nodes: {
               borderWidth: 4,
               shape: 'dot',
               font: {
                 size: 20,
                 face: 'Tahoma'
               },
               scaling: {
                 min: 10,
                 max: 30,
                 label: {
                   min: 8,
                   max: 30,
                   drawThreshold: 12,
                   maxVisible: 20
                 }
               },
               size: 16
           },
           edges:{
             width: 0.15,
             smooth: {
               "type": "continuous",
               "forceDirection": "none",
               "roundness": 0.15
             },
             physics: true

           },
           layout: {
               improvedLayout:true,
               hierarchical: {
                 enabled:false,
                 levelSeparation: 150,
                 direction: 'UD',   // UD, DU, LR, RL
                 sortMethod: 'hubsize' // hubsize, directed
               },
               randomSeed:780555
           },
           interaction:{
             hideEdgesOnDrag: true,
             hover:true,
             tooltipDelay: 300
           },
            physics: {
                barnesHut: {
                gravitationalConstant: -15000,
                centralGravity: 4.55,
                springLength: 155,
                springConstant: 0.15,
                damping: 0.31,
                avoidOverlap: 0.55
            },
                minVelocity: 0.75
            }
/*           physics: {
             stabilization: false,
             barnesHut: {gravitationalConstant: -8000, springConstant: 0.012, springLength: 100},
             maxVelocity: 8,
             minVelocity: 5,
             solver: 'barnesHut',
             adaptiveTimestep: true,
             stabilization: {
               enabled: true,
               iterations: 1000,
               updateInterval: 100,
               onlyDynamicEdges: false,
               fit: true
             }
           }
           */
         };

         $('#heatmapIsLoading').html('<span class="fa fa-spinner fa-2x fa-pulse"></span>');
         var nodeArray = [];
         var geneColorArray = [];
         var result = scope.result;
         for(var i=0; i<result.nodes.length; i++){

           rgbString = 'rgb(' + Math.floor(result.nodes[i].rfrac) + ',' + Math.floor(result.nodes[i].gfrac) + ',' + Math.floor(result.nodes[i].bfrac) + ')'

           var node_degree = result.nodes[i].degree > 30 ? 30 + ((result.nodes[i].degree - 30)/6) : result.nodes[i].degree;
           node_degree = node_degree < 10 ? 10 : node_degree;
           var font_size = result.nodes[i].degree * 2;
           font_size = font_size < 10 ? 10 : font_size;
           //if(scope.geneList.indexOf(result.nodes[i].id) > -1) {
        //       geneColorArray.push(rgbString + "query");
        //     nodeArray.push({id: i, label: result.nodes[i].id, title: 'Testing', font: {size: 99}, permaLabel: result.nodes[i].id, color: rgbString, permaColor: rgbString, shape: 'square', size: 22, permaSize: 20});
        //     scope.dropdownGeneNodes.push({id: i, label: result.nodes[i].id, color: rgbString});
        //   } else {
               geneColorArray.push(rgbString);
              if(result.nodes[i].node_type === "DRUGABLE"){
                  if(result.nodes[i].seed_gene){
                      //QueryGeneDot
                      nodeArray.push({id: i, label: result.nodes[i].node_info, title: result.nodes[i].pop_up_info, font: {size: 30, color: 'black'}, color: {'border': '#000000'}, permaColor: {'background':rgbString, 'border': '#000000'}, shape: 'circularImage', image: '../images/QueryGeneDot.png', size: node_degree, permaSize: node_degree});
                  } else {
                      nodeArray.push({id: i, label: result.nodes[i].node_info, title: result.nodes[i].pop_up_info, font: {size: 30, color: result.nodes[i].font_color}, color: {'background':rgbString, 'border': '#000000'}, permaColor: {'background':rgbString, 'border': '#c0c0c0'}, shape: 'dot', size: node_degree, permaSize: node_degree});
                  }
              }
              else
              {
                  if(result.nodes[i].seed_gene){
                      nodeArray.push({id: i, label: result.nodes[i].node_info, title: result.nodes[i].pop_up_info, font: {size: 30}, color: {'background':rgbString, 'border': 'yellow'}, permaColor: {'background':rgbString, 'border': '#c0c0c0'}, shape: 'dot', size: node_degree, permaSize: node_degree});
                  }
                  else {
                      nodeArray.push({id: i, label: result.nodes[i].node_info, title: result.nodes[i].pop_up_info, font: {size: 25}, color: {'background':rgbString, 'border': rgbString}, permaColor: {'background':rgbString, 'border': '#c0c0c0'}, shape: 'dot', size: node_degree, permaSize: node_degree});
                  }
              }
             //scope.dropdownAuthorNodes.push({id: i, label: result.nodes[i].id});
          // }
         }
         //nodeArray.push({id: 999999,  shape: 'image', image: './images/heat_prop_drugs_legend.png', size: 100, fixed: true, x: -1300, y: -1000});

         var edgeArray = [];

         var scale = chroma.scale(['blue', 'white', 'red']);

         for(var i=0; i<result.links.length; i++){
           edgeArray.push({
                from: result.links[i].source,
                to: result.links[i].target,
                label: '',

                font: {align: 'horizontal', size: 20, background: 'rgba(255,255,255,255)'},
                title: result.links[i].weight,
                zindex: 1050,
                color: {
                 color: scale(result.links[i].weight + 0.1).hex(),
                 hover: scale(result.links[i].weight + 0.15).hex(),
                 highlight: scale(result.links[i].weight + 0.15).hex(),
                 opacity: (Math.abs(result.links[i].weight) - 0.15)
                }
             }
           );
         }

          scope.nodes = new vis.DataSet(nodeArray);
          scope.edges = new vis.DataSet(edgeArray);

          scope.nodeArray = nodeArray;
          scope.edgeArray = edgeArray;

          // create a network
          var container = document.getElementById('heatmap');
          var data = {
            edges: scope.edges,
            nodes: scope.nodes
          };
          var options = {};
          scope.network = new vis.Network(container, data, vizOptions);

          scope.allNodes = scope.nodes.get({returnType:"Object"});
          scope.allEdges = scope.edges.get({returnType:"Object"});

          scope.network.fit();
          $('#heatmapIsLoading').html('');
          scope.network.on("afterDrawing", function (params) {
              if(!scope.info.doneRendering){
                  scope.info.doneRendering = true;
                  scope.network.setOptions({physics: {enabled: false}});
              }
          });

    }

    return {
      scope: {
          result: "="
      },
      restrict: "EA",
      template:
//            "<p>{{result}}</p>" +
            "<style>" +
            ".col-xs-12-custom, .col-xs-9-custom, .col-xs-3-custom {" +
            "    position: relative;" +
            "    min-height: 1px;" +
            "    padding-right: 2px;" +
            "    padding-left: 2px;" +
            "}" +
            ".col-xs-12-custom, .col-xs-9-custom, .col-xs-3-custom {" +
            "    float: left;" +
            "}" +
            ".col-xs-12-custom {" +
            "    width: 100%;" +
            "}" +
            ".col-xs-9-custom {" +
            "    width: calc(100% - 370px);" +
            "}" +
            ".col-xs-3-custom {" +
            "    width: 370px;" +
            "}" +
            "</style>" +
            "<h3>First attempt at inferred drug evidence viz:</h3>" +
            "<div ng-init='showgraphSidebar = false' style='margin-right: 30px;'>" +
            "<div  ng-class='showgraphSidebar ? \"col-xs-9-custom\" : \"col-xs-12-custom\"'>" +
                "<button class='btn btn-primary btn-xs pull-right hidden-xs' style='margin-top: 5px; margin-bottom: 0px; margin-right: 1px; background-color: #f5f5f5; border-color: #e3e3e3; color: black;' ng-show='!showgraphSidebar'>LEGEND</button>" +
                "<button class='btn btn-primary btn-xs pull-right hidden-xs' style='margin-top: 5px; margin-bottom: 0px; margin-right: 1px;' ng-click='showgraphSidebar = !showgraphSidebar'>" +
                "    <span class='fa fa-angle-double-left fa-lg' ng-show='!showgraphSidebar'></span>" +
                "    <span class='fa fa-angle-double-right fa-lg' ng-show='showgraphSidebar'></span>" +
                "</button>" +
              "<div id='heatmapIsLoading' style='width: 200px;'></div>" +
              "<div id='heatmap' style='height: 600px; width: 100%; margin-bottom: 15px; margin-left: 10px; margin-top: 0px;'></div>" +
            "</div>" +
            "<div  ng-class='showgraphSidebar ? \"col-xs-3-custom\" : \"hidden\"'><img src='images/heat_prop_drugs_legend.png' /></div>" +
            "</div>" +
            "<div style='clear:both;'></div>",
      link: link
    };
});


/*
==========================================
==========================================
        CONDITIONS
        LINKS
==========================================
==========================================
*/
app.directive('conditionLinks', function () {
    function link(scope, el, attrs) {
        scope.info = {
          "doneRendering": false
        };
    }

    return {
      scope: {
          tissue: "=",
          result: "=",
          linkids: "=",
          ctype: "="
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/conditions_directive.html",
/*      template:
          "<span class='dropdown' ng-if='ctype === \"CLINVARX\"'>"
        + "  <a style='cursor: pointer;' data-toggle='dropdown'>{{tissue}}</a>"
        //+ "  <button class='btn btn-link dropdown-toggle' type='button' data-toggle='dropdown'>{{tissue}} <i class='fa fa-info-circle' aria-hidden='true'></i></button>"
        + "  <ul class='dropdown-menu'>"
        + "    <li ng-repeat='linkid in linkids'>"
        + "       <a ng-repeat='(key, value) in linkid' ng-if='key == \"MedGen\"' href='http://www.ncbi.nlm.nih.gov/medgen/?term={{value}}' target='_blank'>MedGen ({{value}})</a>"
        //+ "       <a ng-repeat='(key, value) in linkid' ng-if='key == \"SNOMED CT\"' href='http://www.ncbi.nlm.nih.gov/medgen/?term={{value}}' target='_blank'>SNOMED ({{value}})</a>"
        + "       <a ng-repeat='(key, value) in linkid' ng-if='key == \"OMIM\"' href='http://omim.org/entry/{{value}}' target='_blank'>OMIM ({{value}})</a>"
        + "    </li>"
        + "  </ul>"
        + "</span>"
        + "<span ng-if='ctype === \"CLINVAR\"' ng-repeat='linkid in linkids'>"
        + "    <a ng-repeat='(key, value) in linkid' ng-if='key == \"MedGen\"' href='http://www.ncbi.nlm.nih.gov/medgen/?term={{value}}' target='_blank'>{{tissue}}</a>"
        + "</span>"
        + "<span class='dropdown' ng-if='ctype === \"COSMIC\"'>"
        + " <a href='https://en.wikipedia.org/wiki/{{tissue}}' target='_blank'>{{tissue}}</a>"
        + "</span>"
        + "<span class='dropdown' ng-if='ctype === \"COSMIC\"'>"
        + "  <a style='cursor: pointer;' data-toggle='dropdown'>{{tissue}}</a>"
        //+ "  <button class='btn btn-link dropdown-toggle' type='button' data-toggle='dropdown'>{{tissue}} <i class='fa fa-info-circle' aria-hidden='true'></i></button>"
        + "  <ul class='dropdown-menu'>"
        + "    <li ng-if='result.length > 0' ng-repeat='item_id in result | orderBy:\"item_id\"'><a href='http://www.ncbi.nlm.nih.gov/pubmed/{{item_id}}' target='_blank'>Pubmed ({{item_id}})</a></li>"
        + "    <li ng-if='result.length < 1' ng-repeat='item_id in linkids | orderBy:\"item_id\"'><a href='http://cancer.sanger.ac.uk/cosmic/mutation/overview?id={{item_id.replace(\"COSM\",\"\")}}' target='_blank'>Cosmic ({{item_id}})</a></li>"
        + "  </ul>"
        + "</span>",
*/
      link: link
    };
});


/*
==========================================
==========================================
        MAIN PAGE
        ABOUT US
        INFORMATION PAGE
==========================================
==========================================
*/
app.directive('mainAbout', function () {
    function link(scope, el, attrs) {

    }

    return {
      scope: {
          showPage: "="
      },
      restrict: "EA",
      templateUrl: "partials/about/mainAboutTemplate.html",
      link: link
    };
});

/*
==========================================
==========================================
        GENE MODULES
        ABOUT US
        INFORMATION PAGE
==========================================
==========================================
*/
app.directive('geneModulesAbout', function () {
    function link(scope, el, attrs) {

    }

    return {
      scope: {showPage: "="},
      restrict: "EA",
      templateUrl: "partials/about/geneModulesAboutTemplate.html",
      link: link
    };
});

/*
==========================================
==========================================
        CONDITIONS
        ABOUT US
        INFORMATION PAGE
==========================================
==========================================
*/
app.directive('conditionsAbout', function () {
    function link(scope, el, attrs) {

    }

    return {
        scope: {showPage: "="},
      restrict: "EA",
      templateUrl: "partials/about/conditionsAboutTemplate.html",
      link: link
    };
});

/*
==========================================
==========================================
        AUTHORS
        ABOUT US
        INFORMATION PAGE
==========================================
==========================================
*/
app.directive('authorsAbout', function () {
    function link(scope, el, attrs) {

    }

    return {
        scope: {showPage: "="},
      restrict: "EA",
      templateUrl: "partials/about/authorsAboutTemplate.html",
      link: link
    };
});

/*
==========================================
==========================================
        DRUGS
        ABOUT US
        INFORMATION PAGE
==========================================
==========================================
*/
app.directive('drugsAbout', function () {
    function link(scope, el, attrs) {

    }

    return {
        scope: {showPage: "="},
      restrict: "EA",
      templateUrl: "partials/about/drugsAboutTemplate.html",
      link: link
    };
});

/*
==========================================
==========================================
        CONDITIONS
        INFORMATION
        DIRECTIVE
==========================================
==========================================
*/
app.directive('conditionInfo', function (HttpServiceJsonp, $timeout) {
    function link(scope, el, attrs) {
        scope.pythonHost = python_host_global;
        scope.info = {
            "pubmedIds": [],
            "cosmicIds": []
        };

        $timeout(function() {
            for(var i=0;i<scope.conditionData["condition_item"].length;i++){
                conditionItem = scope.conditionData["condition_item"][i];

                scope.info.cosmicIds.push(conditionItem["cosmic_id"] + "~" + conditionItem["name"]);
            }
        }, 300);

//        var url = scope.pythonHost + "/api/elasticsearch/getclusterenrichmentbyid/" + esId + "?callback=JSON_CALLBACK";
//        var myrequest = HttpServiceJsonp.jsonp(url)
//             .success(function (result) {
//                  scope.modalData = result;
//             }).finally(function () {
//        }).error(function (data, status, headers, config) {
//            alert(data + ' - ' + status + ' - ' + headers);
//        });
    }

    return {
      scope: {
          conditionData: "="
      },
      restrict: "EA",
      templateUrl: "partials/directiveTemplates/conditions_info_directive.html",
      link: link
    };
});

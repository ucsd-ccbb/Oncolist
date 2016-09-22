
var app = angular.module('myApp', ['elasticsearch', "services", "ui.bootstrap"]);
// elasticsearch.angular.js creates an elasticsearch
// module, which provides an esFactory
app.service('es', function (esFactory) {
    return esFactory({
        //host: 'http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:9200'
        host: 'http://localhost:9200'
    });
});

app.controller('myCtrl', function ($scope, $http, $log, es, HttpServiceJsonp, Icd10Search) {
    $scope.searchbox = "OR2J3, AANAT, CCDC158, PLAC8L1,CLK1,GLTP,PITPNM2,TRAPPC8,EIF2S2,ST14,NXF1,H3F3B, FOSB, MTMR4, USP46, CDH11, ENAH, CNOT7, STK39, CAPZA1, STIM2, DLL4, WEE1, MYO1D, TEAD3";
    $scope.mySearchResults = [];
    $scope.testingJson = "";
    $scope.directSearch = false;
    es.cluster.health(function (err, resp) {
        if (err) {
            alert('Error: ' + err.message);
        }
    });


    /*
     ===============================
     MAIN SEARCH CALL (FROM SEARCH BUTTON)
     ===============================
     */
    $scope.runHttpSearch = function () {
        var searchboxValue = "";
        var termListArray = [];
        angular.forEach($scope.project.term_list, function (value, key) {
            this.push(value["user"]);
        }, termListArray);

        searchboxValue = termListArray.toString();

        if ($scope.directSearch) {
            es.search({
                index: 'network',
                size: 100,
                body:
                        {
                            //fields: ['source', 'nodeName', 'gene_neighborhood.neighbors.name'],
                            query: {
                                match: {
                                    nodeName: searchboxValue
                                }
                            }
                        }
            })
                    .then(function (resp) {
                        $scope.greatestHits = resp.hits.hits;
                        $scope.resultsPresent = "true";
                        $scope.httpSearchResults = resp.hits.hits[0]._source;
                        $scope.multipleResults = resp.hits.hits;
                    });
        } else {
            es.search({
                index: 'network',
                size: 100,
                body:
                        {
                            //fields: ['source', 'nodeName', 'gene_neighborhood.neighbors.name'],
                            query: {
                                match: {
                                    'gene_neighborhood.neighbors.name': searchboxValue
                                }
                            }
                        }
            })
                    .then(function (resp) {
                        $scope.greatestHits = resp.hits.hits;
                        $scope.resultsPresent = "true";
                        $scope.httpSearchResults = resp.hits.hits[0]._source;
                        $scope.multipleResults = resp.hits.hits;
                    });
        }
    };

    //$(function () {
    //   $('[data-toggle="popover"]').popover();
    //})

    $scope.getNeighborhood = function (neighborhoodType, neighborhoodParentIndex) {
        //this.parent.css = class="affix" data-spy="affix" data-offset-top="5"

        $scope.neighborhoodInfo = "true";
        $scope.neighborhoodTitle = neighborhoodType.toUpperCase();
        switch (neighborhoodType) {
            case "gene":
                if ($scope.multipleResults[neighborhoodParentIndex]._source.gene_neighborhood != null) {
                    $scope.showThisNeighborhood = $scope.multipleResults[neighborhoodParentIndex]._source.gene_neighborhood.neighbors;
                    $scope.neighborhoodDisplayType = "btn-success";
                } else {
                    $scope.neighborhoodInfo = "false";
                    alert('no gene');
                }
                break;
            case "pathway":
                if ($scope.multipleResults[neighborhoodParentIndex]._source.pathway_neighborhood != null) {
                    $scope.showThisNeighborhood = $scope.multipleResults[neighborhoodParentIndex]._source.pathway_neighborhood.neighbors;
                    $scope.neighborhoodDisplayType = "btn-warning";
                } else {
                    $scope.neighborhoodInfo = "false";
                    alert('no pathway');
                }
                break;
            case "protein":
                if ($scope.multipleResults[neighborhoodParentIndex]._source.protein_neighborhood != null) {
                    $scope.showThisNeighborhood = $scope.multipleResults[neighborhoodParentIndex]._source.protein_neighborhood.neighbors;
                    $scope.neighborhoodDisplayType = "btn-info";
                } else {
                    $scope.neighborhoodInfo = "false";
                    alert('no protein');
                }
                break;
            case "drug":
                if ($scope.multipleResults[neighborhoodParentIndex]._source.drug_neighborhood != null) {
                    $scope.showThisNeighborhood = $scope.multipleResults[neighborhoodParentIndex]._source.drug_neighborhood.neighbors;
                    $scope.neighborhoodDisplayType = "";
                } else {
                    $scope.neighborhoodInfo = "false";
                    alert('no drug');
                }
                break;
            case "trxfactor":
                if ($scope.multipleResults[neighborhoodParentIndex]._source.trxfactor_neighborhood != null) {
                    $scope.showThisNeighborhood = $scope.multipleResults[neighborhoodParentIndex]._source.trxfactor_neighborhood.neighbors;
                    $scope.neighborhoodDisplayType = "btn-info";
                } else {
                    $scope.neighborhoodInfo = "false";
                    alert('no drug');
                }
                break;
        }
    }







    //===============================
    // CARROT SCRIPTS
    //===============================
    //function doVisualize() {
    $scope.doVisualize = function () {

        var genelistArray = [];
        angular.forEach($scope.project.gene_list, function (value, key) {
            this.push(value["user"]);
        }, genelistArray);

        alert(genelistArray.toString().replace(",", " "));
        //var url = "http://public-api.wordpress.com/rest/v1/sites/wtmpeachtest.wordpress.com/posts?callback=JSON_CALLBACK";
        var url = "http://localhost:8181/api/nav/aaron/BRCA1?callback=JSON_CALLBACK";
        /*
         $http.jsonp(url)
         .success(function (data) {

         alert(data["Uniprot ID"]);
         })
         .error(function (data, status, headers, config) {
         alert(data + ' - ' + status);
         });

         //alert();
         $http.jsonp("http://localhost/api/nav/aaron/BRCA1?callback=CALL_BACK").
         success(function(response) {
         $scope.geneResolver = status;
         }).
         error(function(data, status, headers, config) {
         alert(data + ' - ' + status );
         });


         $http.get("http://localhost:8080/TestWS/json/carrot2.json")
         .success(function (response) {
         //$scope.resultsPresent = "true";
         $scope.httpClusterResults = response.clusters;
         }
         )
         .error(function (data, status, headers, config) {
         alert("Error getting search results");
         });
         */
    };


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
        "gene_list": []
    };

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
        //$scope.save_project();
    };

    // clear the entire gene list and save the project to the server
    $scope.delete_gene_list = function () {
        $scope.project.term_list.length = 0;
        //$scope.save_project();
    };



    function areTermsReadyToProcess(force) {
        var wordsChecker = _.words($scope.dirty.term_list, /[\w0-9\-_]+/g);
        var isReady = false;


        // if there's more than one word, we assume that the user cut and pasted into the input box
        // in this case, we treat the last word as complete rather than waiting for the user to continue typing
        // TODO decide if this behavior is more annoying or useful
        force = force || wordsChecker.length > 1;

        // we might leave the last word alone if the user is still typing
        var last = wordsChecker.slice(-1)[0];
        if (last === undefined) {
            // no word in progress, so clear the input box
            $scope.dirty.term_list = "";
        } else {
            if (!force && $scope.dirty.term_list.slice(-last.length) == last) {
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



    // this method is called on any activity in the gene list input box
    // force is true when the user moves focus away from the input box and causes us to process the entire word
    // otherwise, the user could be in the middle of typing the last word and we wait for them to finish
    $scope.add_terms = function (force) {

        if (areTermsReadyToProcess(force)) {

            var words = $scope.dirty.term_list;

            if (words.length > 0) {
                var url = "http://ec2-52-26-19-122.us-west-2.compute.amazonaws.com:8080/NLP/Classifier/get-direct-term-resolution/" + words + "?callback=JSON_CALLBACK";
                //var url = "http://localhost:8080/NLP/Classifier/get-direct-term-resolution/" + words + "?callback=JSON_CALLBACK";
                //var url = "http://ec2-54-148-99-18.us-west-2.compute.amazonaws.com:8080/NLP/Classifier/get-direct-term-resolution/" + words + "?callback=JSON_CALLBACK";
                $scope.dirty.term_list = "";

                var myrequest = HttpServiceJsonp.jsonp(url)
                        .success(function (result) {
                            //$scope.resultsPresent = "true";

                            $scope.testingJson = result.termClassification;

                            var termResults = result.termClassification;

                            if (Object.prototype.toString.call(termResults) === '[object Array]') {

                                termResults.forEach(function (entry) {
                                    //alert(entry["probabilitiesMap"]["gene"]);
                                    if (entry["probabilitiesMap"]["gene"] > 0.2) {
                                        var term = {'user': entry["termId"], "type": "gene"};
                                        $scope.project.gene_list.push(term);
                                        $scope.project.term_list.push(term);
                                    }

                                    if (entry["probabilitiesMap"]["icd10"] > 0.2) {
                                        var term = {'user': entry["termId"], "type": "icd10"};
                                        $scope.project.gene_list.push(term);
                                        $scope.project.term_list.push(term);
                                    }

                                    if (entry["probabilitiesMap"]["drug"] > 0.2) {
                                        var term = {'user': entry["termId"], "type": "drug"};
                                        $scope.project.gene_list.push(term);
                                        $scope.project.term_list.push(term);
                                    }

                                    if (entry["status"] === 'unknown') {
                                        var term = {'user': entry["termId"], "type": "unknown"};
                                        $scope.project.gene_list.push(term);
                                        $scope.project.term_list.push(term);
                                    }
                                });

                            } else { //NOT AN ARRAY
                                if (termResults["probabilitiesMap"]["gene"] > 0.2) {
                                    var term = {'user': termResults["termId"], "type": "gene"};
                                    $scope.project.gene_list.push(term);
                                    $scope.project.term_list.push(term);
                                }
                                if (termResults["probabilitiesMap"]["icd10"] > 0.2) {
                                    var term = {'user': termResults["termId"], "type": "icd10"};
                                    $scope.project.gene_list.push(term);
                                    $scope.project.term_list.push(term);
                                }
                                if (termResults["probabilitiesMap"]["drug"] > 0.2) {
                                    var term = {'user': termResults["termId"], "type": "drug"};
                                    $scope.project.gene_list.push(term);
                                    $scope.project.term_list.push(term);
                                }

                                if (termResults["status"] === 'unknown') {
                                    var term = {'user': termResults["termId"], "type": "unknown"};
                                    $scope.project.gene_list.push(term);
                                    $scope.project.term_list.push(term);
                                }
                            }


                        }).finally(function () {
                    //alert();
                }).error(function (data, status, headers, config) {
                            alert(data + ' - ' + status + ' - ' + headers);
                        });
            }
        }
    };


    $scope.searchFactoryGo = function (searchTerm) {
        var icd10SearchInstance = new Icd10Search('chol');

        // fetch data and publish on scope
        icd10SearchInstance.getSearchResults().then(function () {

            $scope.icd10FactoryResults = icd10SearchInstance.searchResults;
        });
    };

    $scope.searchICD10 = function (searchTerm, scopevariable) {
        var icd10url = "http://localhost:8181/ontologies/icd10/findbyname/" + searchTerm + "?callback=JSON_CALLBACK";
        var returnResults = [];
        HttpServiceJsonp.jsonp(icd10url)
                .success(function (result) {
                    var differentTypes = "";
                    angular.forEach(result, function (value, key) {
                        returnResults.push(value["name"]);
                    });
                    $scope.mySearchResults = returnResults;
                    //alert(returnResults);
                });
    }

    $scope.selected = undefined;
    $scope.states = [];

    $scope.onedit = function () {

        var icd10SearchInstance = new Icd10Search($scope.selected);

        // fetch data and publish on scope
        icd10SearchInstance.getSearchResults().then(function () {

            //$scope.icd10FactoryResults = icd10SearchInstance.searchResults;
            $scope.states = [];
            angular.forEach(icd10SearchInstance.searchResults, function (value, key) {
                this.push(value["name"]);
            }, $scope.states);
        });
    }



});


document.addEventListener('copy', function (e) {
    var textToPutOnClipboard = "OR2J3,AANAT,lymphatic,CCDC158,PLAC8L1,Caffeine,CLK1,Cholera,GLTP,PITPNM2,TRAPPC8,EIF2S2,adverse,ST14,NXF1,H3F3B,FOSB,MTMR4,USP46,CDH11,ENAH,transplanted,CNOT7,STK39,CAPZA1,STIM2,nasal,DLL4,WEE1,MYO1D,TEAD3";
    e.clipboardData.setData('text/plain', textToPutOnClipboard);
    e.preventDefault();
});

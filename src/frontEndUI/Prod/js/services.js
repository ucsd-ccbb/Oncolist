angular.module("services", [])

        .factory("HttpServiceJsonp", function ($http, $log) {
            /*
             A thin wrapper around angular's $http service that exposes an object for easy display in the UI.

             This API is chained so you can do things like:

             $scope.request = HttpService.get(‘/some/rest/url’)
             .success(…)
             .error(…)
             .finally(…);

             It uses angular’s $log service to log the request, success, or error of each request.

             See also the loading directive and loading html template.
             */

            service = {};

            service.request = function (method, url, data) {
                var self = {
                    method: method.toLowerCase(),
                    url: url,
                    pending: true,
                    fulfilled: false,
                    rejected: false,
                };

                $log.info(self.method + " " + url);

                if (_.includes(["get", "put", "delete"], self.method)) {
                    self.promise = $http[self.method](self.url);
                } else if (self.method == "post") {
                    self.promise = $http.post(self.url, data);
                } else if (self.method == "jsonp") {
                    self.promise = $http.jsonp(self.url);
                } else {
                    $log.error("request method must be 'get', 'put', 'post', or 'delete'");
                }

                self.success = function (f) {
                    self.promise.success(f);
                    return self;
                };

                self.error = function (f) {
                    self.promise.error(f);
                    return self;
                };

                self.then = function (f) {
                    self.promise.then(f);
                    return self;
                };

                self.finally = function (f) {
                    self.promise.finally(f);
                    return self;
                };

                self.success(function (data, status, headers, config) {
                    $log.info(self.method + " " + url + " success");
                    self.pending = false;
                    self.fulfilled = true;
                    //alert(self.method + " " + url + " success");
                });

                self.error(function (data, status, headers, config) {
                    $log.error(self.method + " " + url + " error");
                    self.pending = false;
                    self.rejected = true;
                    self.status = status;
                    //alert('fail');
                });

                return self;
            };

            service.get = _.partial(service.request, 'get');
            service.put = _.partial(service.request, 'put');
            service.post = _.partial(service.request, 'post');
            service.delete = _.partial(service.request, 'delete');
            service.jsonp = _.partial(service.request, 'jsonp');

            return service;
        })
        .factory('Icd10Search', function ($http) {
            // instantiate our initial object
            var Icd10Search = function (searchTerm) {
                this.searchTerm = searchTerm;
                this.searchResults = null;
            };

            Icd10Search.prototype.getSearchResults = function () {
                var self = this;

                return $http.jsonp("http://localhost:8181/ontologies/icd10/findbyname/" + this.searchTerm + "?callback=JSON_CALLBACK")
                .then(function (response) {
                    self.searchResults = response.data
                    return response;
                });
            };

            return Icd10Search;
        })
        .factory('geneSearch', function ($http) {
            // instantiate our initial object
            var geneSearch = function (searchTerm) {
                this.searchTerm = searchTerm;
                this.searchResults = null;
            };

            geneSearch.prototype.getSearchResults = function () {
                var self = this;

                return $http.jsonp("http://localhost:8181/api/nav/aaron/" + this.searchTerm + "?callback=JSON_CALLBACK")
                .then(function (response) {
                    self.searchResults = response.data;
                    return response;
                });
            };

            return geneSearch;
        })
        .factory('termResolver', function ($http) {
            // instantiate our initial object
            var termResolver = function (searchTerm) {
                this.searchTerm = searchTerm;
                this.searchResults = null;
            };

            termResolver.prototype.getSearchResults = function () {
                var self = this;

                return $http.jsonp("http://localhost:8181/ontologies/distinguish/" + this.searchTerm + "?callback=JSON_CALLBACK")
                .then(function (response) {
                    self.searchResults = response.data;
                    return response;
                });
            };

            return termResolver;
        })
        .factory("PollerService", function ($http, $log, $timeout) {

            service.poll = function (f, dt) {
                var poller = {
                    timeout: undefined
                };

                poller.stop = function () {
                    $log.debug('stop polling');
                    $timeout.cancel(poller.timeout);
                    return poller;
                };

                poller.start = function () {
                    f().then(function () {
                        var ms = _.isFunction(dt) ? dt() : dt;
                        if (ms) {
                            $log.debug('polling again in ' + ms + ' ms');
                            poller.timeout = $timeout(poller.start, ms);
                        }
                    });
                    return poller;
                };

                poller.start();

                return poller;
            };

            return service;
        })
        .factory('ClusterSearchService', function($http, $q) {
            function ClusterSearchService() {

                var self = this;

                //===============================
                //===============================
                //===============================
                // ClusterSearchService METHODS
                //===============================
                //===============================
                //===============================
                self.getSearchResults = function(term_list, pageNumber) {
                    //    Create a deferred operation.
                    var deferred = $q.defer();

                    var termListArray = [];
                    var cancerListArray = [];

                    angular.forEach(term_list, function (value, key) {
                        if(value["type"] === 'gene')
                        this.push(value["user"]);
                    }, termListArray);

                    angular.forEach(term_list, function (value, key) {
                        if(value["type"] === 'disease')
                        this.push(value["user"]);
                    }, cancerListArray);

                    searchboxValue = termListArray.toString();
                    cancerTypeValue = cancerListArray.toString().toLowerCase();

                    var url = "";
                    if(cancerTypeValue.length > 0) {
                        url = python_host_global + "/search/clusters/" + searchboxValue+ "/" + pageNumber + "/" + cancerTypeValue + "?callback=JSON_CALLBACK";
                    } else {
                        url = python_host_global + "/search/clusters/" + searchboxValue+ "/" + pageNumber + "?callback=JSON_CALLBACK";
                    }

                    $http.jsonp(url)
                    .success(function(result) {
                        returnObj = [];
                        var hit_ids = "";
                        var inferred_drug_cluster_ids = "";

                        for (i = 0; i < result.length; ++i) {
                            returnItem = {
                                    "result": result[i],
                                    "searchTab": result[i].searchTab,
                                    "hit_ids": "",
                                    "inferred_drug_cluster_ids": "",
                                    "inferred_drug_cluster_ids_with_disease": [],
                                    "clusterFilteredAnnotations": [],
                                    "permaClusterFilteredAnnotations": [],
                                    "clusterAnnotationGOIds": [],
                                    'clusterFilteredMatrixType': [],
                                    'permaClusterFilteredMatrixType': [],
                                    "clusterFilteredDiseases": [],
                                    "permaClusterFilteredDiseases": [],
                                    "clusterFilterDisplayWithCounts": []
                                }

                            // We are attaching the ES _id array to the PATHWAYS JSON Object.
                            if(result[i].searchTab === "PATHWAYS"){
                              returnItem["hit_ids"] = result[i].hit_ids;
                              returnItem["inferred_drug_cluster_ids"] = result[i].hit_ids;
                              returnItem["inferred_drug_cluster_ids_with_disease"] = result[i].hit_ids_with_disease;

                                //==========================================
                                // Add items to the matrix type filter list
                                //==========================================
                                returnItem["clusterFilteredAnnotations"] = result[i].annotation_filter_all;
                                returnItem["permaClusterFilteredAnnotations"] = result[i].annotation_filter_all;

                                returnItem["clusterFilteredMatrixType"] = result[i].matrix_filter_all;
                                returnItem["permaClusterFilteredMatrixType"] = result[i].matrix_filter_all;

                                returnItem["clusterFilteredDiseases"] = result[i].disease_filter_all;
                                returnItem["permaClusterFilteredDiseases"] = result[i].disease_filter_all;

                              if(result[i].grouped_items.length > 0){
                                  for(var j=0;j<result[i].grouped_items.length;j++){
                                      if((result[i].grouped_items[j].groupTopQValue >= 3.5) || (result[i].grouped_items[j].group_title == "Other")){
                                          //returnItem["clusterFilteredAnnotations"].push(result[i].grouped_items[j].group_title);
                                          //returnItem["permaClusterFilteredAnnotations"].push(result[i].grouped_items[j].group_title);
                                          result[i].grouped_items[j].topGOId = result[i].grouped_items[j].topGOId.replace(":","");
                                          returnItem["clusterAnnotationGOIds"].push(result[i].grouped_items[j].topGOId);
                                      }

                                      //==========================================
                                      // Add items to the matrix type filter list
                                      //==========================================
                                      for(var k=0;k<result[i].grouped_items[j].group_members.length;k++){
                                          if(returnItem["clusterFilteredMatrixType"].indexOf(result[i].grouped_items[j].group_members[k].dataSetType) < 0){
                                              //returnItem["clusterFilteredMatrixType"].push(result[i].grouped_items[j].group_members[k].dataSetType);
                                              //returnItem["permaClusterFilteredMatrixType"].push(result[i].grouped_items[j].group_members[k].dataSetType);
                                          }
                                      }
                                  }
                              }

                              if(result[i].diseases.length > 0){
                                  for(var j=0;j<result[i].diseases.length;j++){
                                      //returnItem["clusterFilteredDiseases"].push(result[i].diseases[j].disease_title);
                                      //returnItem["permaClusterFilteredDiseases"].push(result[i].diseases[j].disease_title);
                                      returnItem["clusterFilterDisplayWithCounts"].push(result[i].diseases[j]);
                                  }
                              }
                            }
                            returnObj.push(returnItem);
                        }
                        deferred.resolve(returnObj);
                    })
                    .error(function(response) {
                        deferred.reject(response);
                    });

                    return deferred.promise;
                };
            }

            return new ClusterSearchService();
        })
        .factory('ConditionSearchService', function($http, $q) {
            function ConditionSearchService() {

                var self = this;

                //===============================
                //===============================
                //===============================
                // ConditionSearchService METHODS
                //===============================
                //===============================
                //===============================
                self.getSearchResults = function(term_list, icd10_list, pageNumber) {
                    //    Create a deferred operation.
                    var deferred = $q.defer();

                    var phenotypeTypeValue = "";
                    var termListArray = [];
                    var cancerListArray = [];
                    var phenotypeListArray = [];

                    angular.forEach(term_list, function (value, key) {
                        if(value["type"] === 'gene')
                        this.push(value["user"]);
                    }, termListArray);

                    angular.forEach(term_list, function (value, key) {
                        if(value["type"] === 'disease')
                        this.push(value["user"]);
                    }, cancerListArray);

                    angular.forEach(icd10_list, function (value, key) {
                        if(value["type"] === 'icd10')
                        this.push(value["user"]);
                    }, phenotypeListArray);

                    searchboxValue = termListArray.toString();
                    cancerTypeValue = cancerListArray.toString();
                    phenotypeTypeValue = phenotypeListArray.toString();

                    var url = "";
                    if(phenotypeTypeValue.length > 0) {
                        url = python_host_global + "/nav/clinvar/" + searchboxValue + "/phenotypes/" + phenotypeTypeValue + "?callback=JSON_CALLBACK";
                    } else {
                        url = python_host_global + "/search/phenotypes/" + searchboxValue + "/" + pageNumber + "?callback=JSON_CALLBACK";
                    }

                    $http.jsonp(url)
                    .success(function(result) {
                        returnObj = [];
                        for (i = 0; i < result.length; ++i) {
                            returnItem = {
                                "result": result[i],
                                "searchTab": result[i].searchTab,
                                "conditionsFilter": [],
                                "permaConditionsFilter": [],
                                "tissuesFilter": [],
                                "permaTissuesFilter": []
                            };
                            //======================================
                            // Load the filter array for conditions
                            //======================================
                            if(result[i].searchTab === "PHENOTYPES"){
                                if(result[i].simple_disease_tissue_group.length > 0){
                                    for(var j=0;j<result[i].simple_disease_tissue_group.length;j++){
                                        returnItem["conditionsFilter"].push(result[i].simple_disease_tissue_group[j].disease);
                                        returnItem["permaConditionsFilter"].push(result[i].simple_disease_tissue_group[j].disease);
                                    }
                                }

                                if(result[i].basic_grouped_search_results.tissue_filters.length > 0){
                                    for(var j=0;j<result[i].basic_grouped_search_results.tissue_filters.length;j++){
                                        returnItem["tissuesFilter"].push(result[i].basic_grouped_search_results.tissue_filters[j]);
                                        returnItem["permaTissuesFilter"].push(result[i].basic_grouped_search_results.tissue_filters[j]);
                                    }
                                }
                            }
                            returnObj.push(returnItem);
                        }

                        deferred.resolve(returnObj);
                    })
                    .error(function(response) {
                        deferred.reject(response);
                    });

                    return deferred.promise;
                };
            }

            return new ConditionSearchService();
        })
        .factory('AuthorSearchService', function($http, $q) {
            function AuthorSearchService() {

                var self = this;

                //===============================
                //===============================
                //===============================
                // AuthorSearchService METHODS
                //===============================
                //===============================
                //===============================
                self.getSearchResults = function(term_list, pageNumber) {
                    var deferred = $q.defer();

                    var termListArray = [];

                    angular.forEach(term_list, function (value, key) {
                        if(value["type"] === 'gene')
                        this.push(value["user"]);
                    }, termListArray);

                    searchboxValue = termListArray.toString();

                    //var url = python_host_global + "/api/get/people/peoplecenter2/search/" + searchboxValue + "?callback=JSON_CALLBACK";
                    var url = python_host_global + "/search/authors/" + searchboxValue + "/" + pageNumber + "?callback=JSON_CALLBACK";
console.log(url);
                    $http.jsonp(url)
                    .success(function(result) {
                        returnObj = [];
                        for (i = 0; i < result.length; ++i) {
                            returnItem = {
                                "result": result[i],
                                "searchTab": result[i].searchTab,
                                "authorGeneFilter": [],
                                "permaAuthorGeneFilter": []
                            };

                            //======================================
                            // Load the filter array for conditions
                            //======================================
                    /*
                            if (typeof result[i].overlap_counts != 'undefined'){
                                if(result[i].overlap_counts.length > 0){
                                    for(var j=0;j<result[i].overlap_counts.length;j++){
                                        returnItem["authorGeneFilter"].push(result[i].overlap_counts[j].gene);
                                        returnItem["permaAuthorGeneFilter"].push(result[i].overlap_counts[j].gene);
                                    }
                                }
                            }
                            */

                            for (var k in result[i].geneSuperList) {
                                if (result[i].geneSuperList.hasOwnProperty(k)) {
                                    returnItem["authorGeneFilter"].push(k);
                                    returnItem["permaAuthorGeneFilter"].push(k);
                                }
                            }


                            returnObj.push(returnItem);
                        }

                        deferred.resolve(returnObj);
                    })
                    .error(function(response) {
                        deferred.reject(response);
                    });

                    return deferred.promise;
                };
            }

            return new AuthorSearchService();
        })
        .factory('DrugSearchService', function($http, $q) {
            function DrugSearchService() {

                var self = this;

                //===============================
                //===============================
                //===============================
                // DrugSearchService METHODS
                //===============================
                //===============================
                //===============================
                self.getSearchResults = function(term_list, inferred_drug_cluster_ids_with_disease, disease_to_filter) {
                    //    Create a deferred operation.
                    var deferred = $q.defer();

                    var termListArray = [];
                    var inferred_drug_cluster_ids = "";

                    angular.forEach(term_list, function (value, key) {
                        if(value["type"] === 'gene')
                            this.push(value["user"]);
                    }, termListArray);

                    //===============================================================
                    // If the user provides a disease in the search terms we need
                    // to filter the clusters for inferred drug detection.
                    //===============================================================
                    if(disease_to_filter.length > 0){
                        for(var i=0; i<inferred_drug_cluster_ids_with_disease.length; i++){
                            if(inferred_drug_cluster_ids_with_disease[i]["disease"] === disease_to_filter){
                                inferred_drug_cluster_ids += inferred_drug_cluster_ids_with_disease[i]["id"] + ",";
                            }
                        }
                    }
                    else
                    {
                        for(var i=0; i<inferred_drug_cluster_ids_with_disease.length; i++){
                            inferred_drug_cluster_ids += inferred_drug_cluster_ids_with_disease[i]["id"] + ",";
                        }
                    }

                    if(inferred_drug_cluster_ids.length > 0){
                        inferred_drug_cluster_ids = inferred_drug_cluster_ids.substring(0, inferred_drug_cluster_ids.length - 1);
                    }

                    angular.forEach(inferred_drug_cluster_ids_with_disease, function (value, key) {
                        if(value["type"] === 'gene')
                        this.push(value["user"]);
                    }, inferred_drug_cluster_ids);

                    searchboxValue = termListArray.toString();

                    var url = python_host_global + "/search/drugs/" + searchboxValue + "?callback=JSON_CALLBACK";

                    $http.jsonp(url)
                    .success(function(result) {
                        returnObj = [];
                        for (i = 0; i < result.length; ++i) {
                            returnItem = {
                                "result": result[i],
                                "searchTab": result[i].searchTab,
                                "drugGeneFilter": [],
                                "permaDrugGeneFilter": []
                            };

                            //======================================
                            // Load the filter array for conditions
                            //======================================
                            if (typeof result[i].overlap_counts != 'undefined'){
                                if(result[i].overlap_counts.length > 0){
                                    for(var j=0;j<result[i].overlap_counts.length;j++){
                                        returnItem["drugGeneFilter"].push(result[i].overlap_counts[j].gene);
                                        returnItem["permaDrugGeneFilter"].push(result[i].overlap_counts[j].gene);
                                    }
                                }
                            }

                            returnObj.push(returnItem);
                        }

                        deferred.resolve(returnObj);
                    })
                    .error(function(response) {
                        deferred.reject(response);
                    });

                    return deferred.promise;
                };
            }

            return new DrugSearchService();
        })
        .factory('InferredDrugSearchService', function($http, $q) {
            function InferredDrugSearchService() {

                var self = this;

                //===============================
                //===============================
                //===============================
                // DrugSearchService METHODS
                //===============================
                //===============================
                //===============================
                self.getSearchResults = function(term_list, inferred_drug_cluster_ids_with_disease, disease_to_filter) {
                    //    Create a deferred operation.
                    var deferred = $q.defer();

                    var termListArray = [];
                    var inferred_drug_cluster_ids = "";

                    angular.forEach(term_list, function (value, key) {
                        if(value["type"] === 'gene')
                            this.push(value["user"]);
                    }, termListArray);

                    //===============================================================
                    // If the user provides a disease in the search terms we need
                    // to filter the clusters for inferred drug detection.
                    //===============================================================
                    if(disease_to_filter.length > 0){
                        for(var i=0; i<inferred_drug_cluster_ids_with_disease.length; i++){
                            if(inferred_drug_cluster_ids_with_disease[i]["disease"] === disease_to_filter){
                                inferred_drug_cluster_ids += inferred_drug_cluster_ids_with_disease[i]["id"] + ",";
                            }
                        }
                    }
                    else
                    {
                        for(var i=0; i<inferred_drug_cluster_ids_with_disease.length; i++){
                            inferred_drug_cluster_ids += inferred_drug_cluster_ids_with_disease[i]["id"] + ",";
                        }
                    }

                    if(inferred_drug_cluster_ids.length > 0){
                        inferred_drug_cluster_ids = inferred_drug_cluster_ids.substring(0, inferred_drug_cluster_ids.length - 1);
                    }

                    angular.forEach(inferred_drug_cluster_ids_with_disease, function (value, key) {
                        if(value["type"] === 'gene')
                        this.push(value["user"]);
                    }, inferred_drug_cluster_ids);

                    searchboxValue = termListArray.toString();

                    var url = python_host_global + "/search/inferred/drugs/" + searchboxValue + "/" + inferred_drug_cluster_ids + "?callback=JSON_CALLBACK";

                    $http.jsonp(url)
                    .success(function(result) {
                        returnObj = [];
                        returnItem = {};
                        console.log(result);
                        if(result.inferred_drugs.length > 0){
                            returnItem = {
                                "result": result.inferred_drugs,
                                "searchTab": "DRUG",
                                "drugGeneFilter": [],
                                "permaDrugGeneFilter": [],
                                "annotate_cluster_info": result.annotate_cluster_info
                            };
                        } else {
                            returnItem = {
                                "result": [],
                                "searchTab": "DRUG",
                                "drugGeneFilter": [],
                                "permaDrugGeneFilter": [],
                                "annotate_cluster_info": {}
                            };
                        }

                        //returnObj.push(returnItem);

                        deferred.resolve(returnItem);
                    })
                    .error(function(response) {
                        deferred.reject(response);
                    });

                    return deferred.promise;
                };
            }

            return new InferredDrugSearchService();
        })
        .factory('GenericSearchService', function($http, $q) {
            function GenericSearchService() {

                var self = this;

                //===============================
                //===============================
                //===============================
                // ClusterSearchService METHODS
                //===============================
                //===============================
                //===============================
                self.getSearchResults = function(term_list) {
                    //    Create a deferred operation.
                    var deferred = $q.defer();

                    var url = python_host_global + "/nav/clinvar/" + searchboxValue + "/phenotypes/" + phenotypeTypeValue + "?callback=JSON_CALLBACK";

                    $http.jsonp(url)
                    .success(function(result) {
                        returnObj = [];
                        for (i = 0; i < result.length; ++i) {
                            returnItem = {
                                "result": result[i],
                                "searchTab": result[i].searchTab,
                                "conditionsFilter": [],
                                "permaConditionsFilter": []
                            };
                            //======================================
                            // Load the filter array for conditions
                            //======================================
                            if(result[i].searchTab === "PHENOTYPES"){
                                if(result[i].grouped_by_conditions.length > 0){
                                    for(var j=0;j<result[i].grouped_by_conditions.length;j++){
                                        returnItem["conditionsFilter"].push(result[i].grouped_by_conditions[j].group_condition_type_key);
                                        returnItem["permaConditionsFilter"].push(result[i].grouped_by_conditions[j].group_condition_type_key);
                                    }
                                }
                            }
                            returnObj.push(returnItem);
                        }

                        deferred.resolve(returnObj);
                    })
                    .error(function(response) {
                        deferred.reject(response);
                    });

                    return deferred.promise;
                };
            }

            return new GenericSearchService();
        });

/*        app.controller('MainController', function ($scope, NameService) {

            //    We have a name on the code, but it's initially empty...
            $scope.name = "";

            //    We have a function on the scope that can update the name.
            $scope.updateName = function() {
                NameService.getName()
                    .then(
                        // success function
                        function(name) {
                            $scope.name = name;
                        },
                        // error function
                        function(result) {
                            console.log("Failed to get the name, result is " + result);
                    });
            };
        });
*/

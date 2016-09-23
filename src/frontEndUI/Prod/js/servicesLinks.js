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

                if (self.method == "jsonp") {
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
        });


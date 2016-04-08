function marcos_pos_device(instance, module) {
    var _t = instance.web._t;
    module.ProxyDevice = module.ProxyDevice.extend({

        print_receipt: function (receipt) {
            var self = this;
            if (receipt) {
                this.receipt_queue.push(receipt);
            }
            var aborted = false;
            function send_printing_job() {
                console.log("send_printing_job");
                if (self.receipt_queue.length > 0) {
                    var r = self.receipt_queue.shift();
                    var params  = {};
                    params.receipt = r;
                    params.ipf_odoo = self.pos.config.ipf_odoo;
                    params.ipf_ip = self.pos.config.ipf_ip;
                    params.ipf_host = self.pos.config.ipf_host;


                    if (self.pos.config.ipf_odoo && self.pos.config.ipf_ip ){
                        self.message('print_ipf_receipt', params, {timeout: 5000})
                        .then(function () {
                            send_printing_job();
                        }, function (error) {
                            if (error) {
                                self.pos.pos_widget.screen_selector.show_popup('error-traceback', {
                                    'message': _t('Printing Error: ') + error.data.message,
                                    'comment': error.data.debug
                                });
                                return;
                            }
                            self.receipt_queue.unshift(r)
                        });
                    } else {
                        self.message('print_xml_receipt', {receipt: r}, {timeout: 5000})
                        .then(function () {
                            send_printing_job();
                        }, function (error) {
                            if (error) {
                                self.pos.pos_widget.screen_selector.show_popup('error-traceback', {
                                    'message': _t('Printing Error: ') + error.data.message,
                                    'comment': error.data.debug
                                });
                                return;
                            }
                            self.receipt_queue.unshift(r)
                        });
                    }

                }
            }

            if (self.pos.config.ipf_printer) {
                //var order = self.pos.get('selectedOrder');
                //
                //if (order) {
                //    new instance.web.Model("ipf.printer.config")
                //    .call("print_precuenta", [order.export_as_JSON()])
                //}

            } else {
                send_printing_job();
                console.log("send_printing_job");
            }

        },
        message : function(name,params){
            var callbacks = this.notifications[name] || [];
            for(var i = 0; i < callbacks.length; i++){
                callbacks[i](params);
            }

            if(this.get('status').status !== 'disconnected' && this.pos.config.ipf_odoo){
                return this.connection.rpc('/hw_proxy/' + name, params || {});
            }else{
                return (new $.Deferred()).reject();
            }
        },
        // try several time to connect to a known proxy url
        try_hard_to_connect: function(url,options){
            options   = options || {};
            var port  = ':' + (options.port || '8069');

            this.set_connection_status('connecting');

            if(url.indexOf('//') < 0){
                url = 'http://'+url;
            }

            if(url.indexOf(':',5) < 0){
                url = url+port;
            }

            // try real hard to connect to url, with a 1sec timeout and up to 'retries' retries
            function try_real_hard_to_connect(url, retries, done){

                done = done || new $.Deferred();

                var c = $.ajax({
                    url: url + '/hw_proxy/hello',
                    method: 'GET',
                    timeout: 1000,
                })
                .done(function(){
                    done.resolve(url);
                })
                .fail(function(){
                    if(retries > 0){
                        try_real_hard_to_connect(url,retries-1,done);
                    }else{
                        done.reject();
                    }
                });
                return done;
            }

            return try_real_hard_to_connect(url,3);
        },
        // returns as a deferred a valid host url that can be used as proxy.
        // options:
        //   - port: what port to listen to (default 8069)
        //   - progress(fac) : callback for search progress ( fac in [0,1] )
        find_proxy: function(options){
            options = options || {};
            var self  = this;
            var port  = ':' + (options.port || '8069');
            var urls  = [];
            var found = false;
            var parallel = 8;
            var done = new $.Deferred(); // will be resolved with the proxies valid urls
            var threads  = [];
            var progress = 0;


            urls.push('http://localhost'+port);
            for(var i = 0; i < 256; i++){
                urls.push('http://192.168.0.'+i+port);
                urls.push('http://192.168.1.'+i+port);
                urls.push('http://10.0.0.'+i+port);
            }

            var prog_inc = 1/urls.length;

            function update_progress(){
                progress = found ? 1 : progress + prog_inc;
                if(options.progress){
                    options.progress(progress);
                }
            }

            function thread(done){
                var url = urls.shift();

                done = done || new $.Deferred();

                if( !url || found || !self.searching_for_proxy ){
                    done.resolve();
                    return done;
                }

                var c = $.ajax({
                        url: url + '/hw_proxy/hello',
                        method: 'GET',
                        timeout: 400,
                    }).done(function(){
                        found = true;
                        update_progress();
                        done.resolve(url);
                    })
                    .fail(function(){
                        update_progress();
                        thread(done);
                    });

                return done;
            }

            this.searching_for_proxy = true;

            for(var i = 0, len = Math.min(parallel,urls.length); i < len; i++){
                threads.push(thread());
            }

            $.when.apply($,threads).then(function(){
                var urls = [];
                for(var i = 0; i < arguments.length; i++){
                    if(arguments[i]){
                        urls.push(arguments[i]);
                    }
                }
                done.resolve(urls[0]);
            });

            return done;
        },
        // starts a loop that updates the connection status
        keepalive: function(){
            if (this.pos.config.ipf_odoo){


            var self = this;
            var ipf_odoo = self.pos.config.ipf_odoo;
            var ipf_ip = self.pos.config.ipf_ip;
            var params  = {};
            if (ipf_odoo){
                params.ipf_odoo = ipf_odoo;
                params.ipf_ip = ipf_ip;
            }
            if(!this.keptalive){
                this.keptalive = true;
                function status(){
                    self.connection.rpc('/hw_proxy/status_json',{ipf_odoo: params, ipf_ip: ipf_ip},{timeout:2500})
                        .then(function(driver_status){
                            if (self.pos.config.ipf_odoo && self.pos.config.ipf_ip ){
                                self.set_connection_status(driver_status.status, driver_status);
                            } else {
                                self.set_connection_status('connected',driver_status);
                            }
                        },function(){
                            if(self.get('status').status !== 'connecting'){
                                self.set_connection_status('disconnected');
                            }
                        }).always(function(){
                            setTimeout(status,5000);
                        });
                }
                status();
            };
                }
        },
        set_connection_status: function(status, drivers){
            var self = this;
            oldstatus = this.get('status');
            newstatus = {};
            newstatus.status = status;

            if (self.pos.config === undefined) {
                return
            }

            if (self.pos.config.ipf_odoo && self.pos.config.ipf_ip ){
                newstatus.drivers = status === 'disconnected' ? {} : oldstatus.drivers;
                newstatus.drivers = drivers ? drivers : newstatus.status;
            } else {
                newstatus.drivers = status === 'disconnected' ? {} : oldstatus.drivers;
                newstatus.drivers = drivers ? drivers : newstatus.drivers;
            }
            this.set('status',newstatus);
        }
    });


}
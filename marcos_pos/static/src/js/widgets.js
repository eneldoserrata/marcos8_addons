function marcos_pos_widgets(instance, module) {

    var _t = instance.web._t;

    module.PosWidget = module.PosWidget.extend({
        init: function() {
            this._super(arguments[0],{});
            this.standard_mode = true;
        },
        build_widgets: function (parent, name) {
            var self = this;
            this._super(parent);
            //this.manager = false;
            //this.user_before_manager = false;
            this.marcos_textarea_popup_widget = new module.MarcosTextAreaPopupWidget(this, {});
            this.marcos_input_popup_widget = new module.MarcosInputPopupWidget(this, {});
            this.marcos_product_available_popup_widget = new module.MarcosProductAvailablePopupWidget(this, {});
            this.marcos_textarea_popup_widget.appendTo($(this.$el));
            this.marcos_input_popup_widget.appendTo($(this.$el));
            this.marcos_product_available_popup_widget.appendTo($(this.$el));
            this.screen_selector.popup_set['marcos_input_popup_widget'] = this.marcos_input_popup_widget;
            this.screen_selector.popup_set['marcos_product_available_popup_widget'] = this.marcos_product_available_popup_widget;
            this.screen_selector.popup_set['marcos_textarea_popup_widget'] = this.marcos_textarea_popup_widget;
            // Hide the popup because all pop up are displayed at the
            // beginning by default
            this.marcos_input_popup_widget.hide();
            this.marcos_product_available_popup_widget.hide();
            this.marcos_textarea_popup_widget.hide();


            this.quotation_button = new module.MarcosHeaderButtonWidget(this, {
                class: 'fa fa-file-text-o fa-lg',
                action: function () {
                    self.quotation();
                }
            });

            this.quotation_button.appendTo(this.$('.pos-rightheader'));

            //open opoup to change user by click the cashier name un top
            $(".username").wrap("<a>").parent().click(function(){
                self.change_user();
            });

            if (!self.pos.config.payment_pos) {

                this.cahier_button = new module.MarcosHeaderButtonWidget(this, {
                    class: 'fa fa-money fa-lg',
                    action: function () {
                        self.get_orders({action: "pay"});
                    }
                });

                this.cahier_button.appendTo(this.$('.pos-rightheader'));
            }

            this.refund_button = new module.MarcosHeaderButtonWidget(this, {
                class: 'fa fa-undo fa-lg',
                action: function () {
                    self.get_orders({action: "refund"});
                }
            });

            this.refund_button.appendTo(this.$('.pos-rightheader'));

        },
        change_user: function () {
            var self = this;
            if (self.pos.manager) {
                _.each(self.pos.users, function (user) {
                    if (user.id === self.pos.user_before_manager) {
                        self.pos.barcode_reader.scan(user.ean13);
                        self.pos.user_before_manager = false;
                        self.pos.manager = false;
                        self.pos.manger_validated = false;
                        self.pos.manger_permission = false;
                        self.pos_widget.numpad.state.set('mode', "quantity");
                        self.pos_widget.numpad.changedMode();

                    }
                });
                $(".username").css("color", "white").css("font-size", "19px");
                return
            }

            self.screen_selector.show_popup('marcos_input_popup_widget', {
            message: "Introduzca su clave.",
            input_type: "pwd",
            confirm: function () {
                self.pos.validate_user(this.$("#password").val());
                }
            });

        },
        can_refund: function () {
            var self = this;
            self.pos.validate_manager();
            return self.pos.manger_permission.refund;
        },
        get_orders: function (options) {
            var self = this;
            if (options.action === "refund") {
                var domain = [['state', 'in', ['invoiced']]]
                if (!self.can_refund()) {
                    self.pos.pos_widget.screen_selector.show_popup('error', {
                        'message': _t('Acceso negado'),
                        'comment': _t('No tiene permiso hacer devoluciones!')
                    });
                    return
                }
            } else if (options.action === "pay") {
                var domain = [['state', 'in', ['draft']]]
            }
            pop = new instance.web.form.SelectCreatePopup(this);

            pop.init_dataset = function() {
                var self = this;
                this.created_elements = [];
                this.dataset = new instance.web.ProxyDataSet(this, this.model, this.context);
                this.dataset.read_function = this.options.read_function;
                this.dataset.create_function = function(data, options, sup) {
                    var fct = self.options.create_function || sup;
                    return fct.call(this, data, options).done(function(r) {
                        self.trigger('create_completed saved', r);
                        self.created_elements.push(r);
                    })
                };
                this.dataset.write_function = function(id, data, options, sup) {
                    var fct = self.options.write_function || sup;
                    return fct.call(this, id, data, options).done(function(r) {
                        self.trigger('write_completed saved', r);
                    });
                };
                this.dataset.parent_view = this.options.parent_view;
                this.dataset.child_name = this.options.child_name;
            };
            pop.select_element(
                "pos.order",
                {
                    title: "Buscar orden",
                    initial_view: "search",
                    disable_multiple_selection: true,
                    list_view_options: {limit: 14}
                },
                domain,
                {'search_default_customer': true}
            );

            pop.on("elements_selected", self, function (element_ids) {
                self.load_order(element_ids, options)
            });
        },
        load_order: function (element_ids, options) {
            var self = this;
            var action = options.action;
            var currentOrder = undefined;

            new instance.web.Model("pos.order")
                .call("search_read", {domain: [["id", "=", element_ids[0]]], fields: []})
                .then(function (result) {
                    if (result && result.length == 1) {
                        var partner = self.pos.db.get_partner_by_id(result[0].partner_id[0]);
                        if (options.action === "refund") {
                            self.pos.add_new_order("refund");
                            currentOrder = self.pos.get('selectedOrder');
                            currentOrder.set_client(partner);
                            currentOrder.set("type", "refund");
                            currentOrder.set("refund_order_id", result[0].id);
                        } else {
                            self.pos.add_new_order("payment");
                            currentOrder = self.pos.get('selectedOrder');
                            currentOrder.set_client(partner);
                            currentOrder.set("pos_reference", result[0].pos_reference);
                            currentOrder.set("name", result[0].pos_reference);
                            currentOrder.uid = result[0].pos_reference;
                        }
                        new instance.web.Model("pos.order.line")
                            .call("search_read", {domain: [["order_id", "=", element_ids[0]]], fields: []})
                            .then(function (result) {
                                if (result) {
                                    var products = [];
                                    _.each(result, function (res) {
                                        var product = self.pos.db.get_product_by_id(res.product_id[0]);
                                        var options = {
                                            quantity: res.qty,
                                            price: res.price_unit,
                                            discount: res.discount,
                                        };

                                        if (action === "pay") {
                                            currentOrder.set("load_order", true);
                                            currentOrder.addProduct(product, options);

                                        } else if (action === "refund") {
                                            product.qty_available = res.qty - res.return_qty;
                                            product.origin_id = res.id;
                                            product.refund_price = res.price_unit;
                                            product.refund_discount = res.discount;
                                        }

                                        products.push(product);

                                    });
                                    currentOrder.set("refund_products", products);
                                    self.product_screen.product_list_widget.set_product_list(products);
                                }
                            })
                    }
                })
        },
        quotation: function () {
            var self = this;
            var currentOrder = self.pos.get('selectedOrder');

            if (currentOrder.get('orderLines').models.length === 0) {
                pop = new instance.web.form.SelectCreatePopup(this);
                pop.select_element(
                    "sale.order",
                    {
                        title: "Buscar cotización",
                        initial_view: "search",
                        disable_multiple_selection: true,
                        list_view_options: {limit: 14}
                    },
                    [['state', 'in', ['draft', 'sent']]],
                    {'search_default_customer': true}
                );
                pop.on("elements_selected", self, function (element_ids) {
                    self.load_quotation(currentOrder, element_ids)
                });

            } else {
                self.pos_widget.screen_selector.show_popup("confirm", {
                    'message': 'Como desea entregar esta cotización?',
                    'confirm': function () {
                        self.print_quotation();
                    },
                    'cancel': function () {
                        self.mail_quotation()
                    }
                });

            }

            self.$el.find(".popup-confirm").css('height', '130px');
            self.$el.find(".popup-confirm .footer .button.confirm").html("<i class='fa fa-file-text-o'></i> Impresora");
            self.$el.find(".popup-confirm .footer .button.cancel").html("<i class='fa fa-envelope'></i> Correo");
            self.$el.find(".popup-confirm .footer").append("<div class='button close_dialog'><i class='fa fa-ban'></i> Cancelar</div>");
            self.$el.find(".popup-confirm .footer .button.close_dialog").click(function () {
                self.pos_widget.screen_selector.close_popup();
            });


        },
        load_quotation: function (currentOrder, element_ids) {
            var self = this;
            new instance.web.Model("sale.order")
                .call("search_read", {domain: [["id", "=", element_ids[0]]], fields: []})
                .then(function (result) {
                    if (result && result.length == 1) {
                        var partner = self.pos.db.get_partner_by_id(result[0].partner_id[0]);
                        currentOrder.set_client(partner);

                        new instance.web.Model("sale.order.line")
                            .call("search_read", {domain: [["order_id", "=", element_ids[0]]], fields: []})
                            .then(function (result) {
                                if (result) {
                                    var products = [];
                                    _.each(result, function (res) {
                                        var product = self.pos.db.get_product_by_id(res.product_id[0]);
                                        var options = {
                                            quantity: res.product_uom_qty,
                                            price: res.price_unit,
                                            discount: res.discount,
                                            quotation: true
                                        };
                                        currentOrder.addProduct(product, options);
                                        products.push(product);

                                    });

                                    self.product_screen.product_list_widget.set_product_list(products);

                                }
                            });
                    }
                })
                .fail(function(err, event){
                       event.preventDefault();
                        self.pos_widget.screen_selector.show_popup('error',{
                            'message':_t('Funcionalidad inactiva'),
                            'comment':_t('Es accion requiere conexion al servidor!.')
                        });
                    });

        },
        print_quotation: function () {
            var self = this;
            self.pos_widget.payment_screen.validate_order({action: "print_quotation"});
        },
        mail_quotation: function () {
            var self = this;
            self.pos_widget.payment_screen.validate_order({action: "send_quotation"});
        },
        set_nc_mode: function(visible) {
            var self = this;
            var refund_products = self.pos.get('selectedOrder').get("refund_products");

            if(visible !== this.standard_mode){
                this.standard_mode = visible;
                if(visible){
                    this.numpad.show();
                    this.paypad.show();
                    $(this.product_screen.product_categories_widget.el).show();
                    this.$('.control-buttons').removeClass('oe_hidden');
                    $('.pos .order-button.selected').css("background", "#EEEEEE");
                    this.nc_button.destroy();
                }else{
                    this.numpad.hide();
                    this.paypad.hide();
                    $(this.product_screen.product_categories_widget.el).hide();
                    this.$('.control-buttons').addClass('oe_hidden');
                    $('.pos .order-button.selected').css("background", "#96CA3D");

                    if (refund_products !== undefined) {
                        self.product_screen.product_list_widget.set_product_list(refund_products);
                    }


                    this.nc_button = new module.MarcosPaypadButtonWidget(this, {
                        caption: "Crear nota de crédito",
                        action: function () {
                            self.nc_validate();
                    }
                    });
                    this.nc_button.appendTo(this.$('.control-buttons-special'));
                }
            }
        },
        nc_validate: function(){
            var self = this;
            self.payment_screen.validate_order();
        }

    });

    module.OrderWidget = module.OrderWidget.extend({
        init: function (parent, options) {
            var self = this;
            this._super(parent, options);
            this.summary_selected = false;

            var line_click_handler = this.line_click_handler;
            this.line_click_handler = function (event) {
                self.deselect_summary();
                line_click_handler.call(this, event)
            }
        },
        select_summary: function () {
            if (this.summary_selected)
                return;
            this.deselect_summary();
            this.summary_selected = true;
            $('.order .summary').addClass('selected')
            this.pos_widget.numpad.state.reset();
            this.pos_widget.numpad.state.changeMode('discount');
        },
        deselect_summary: function () {
            this.summary_selected = false;
            $('.order .summary').removeClass('selected')
        },
        set_value: function (val) {
            var mode = this.numpad_state.get('mode');
            var order = this.pos.get('selectedOrder');

            if (mode == 'discount' && this.summary_selected) {
                var order = this.pos.get('selectedOrder');
                $.each(order.get('orderLines').models, function (k, line) {
                    line.set_discount(val)
                })
            } else if (this.editable && order.getSelectedLine()) {
                var mode = this.numpad_state.get('mode');
                if (mode === 'price') {
                    order.getSelectedLine().set_manuel_price(true);
                }
            }

            this._super(val);
        },
        renderElement: function (scrollbottom) {
            var self = this;
            this._super(scrollbottom);

            $('.order .summary').click(function (event) {
                if (!self.editable) {
                    return;
                }
                self.pos.get('selectedOrder').deselectLine(this.orderline);
                self.pos_widget.numpad.state.reset();

                self.select_summary()
            })
        }
    });

    module.NumpadWidget = module.NumpadWidget.extend({

        clickChangeMode: function (event) {
            var self = this;
            var newMode = event.currentTarget.attributes['data-mode'].nodeValue;
            if (newMode != 'price') {
                return this.state.changeMode(newMode);
            }
            else if (newMode === 'price' && self.can_change_price()) {
                return this.state.changeMode(newMode);
            } else {
                self.pos.pos_widget.screen_selector.show_popup('error', {
                    'message': _t('Acceso negado'),
                    'comment': _t('No tiene permiso para cambiar el precio!')
                });
            }
        },
        can_change_price: function () {
            var self = this;
            self.pos.validate_manager();
            return self.pos.manger_permission.change_price;
        }
    });

    module.PaypadWidget = module.PosBaseWidget.extend({
        template: 'PaypadWidget',
        renderElement: function () {
            var self = this;
            this._super();
            var currentOrder = self.pos.get('selectedOrder');
            var payment_pos = self.pos.config.payment_pos;

            // sort cashregisters by sequence
            this.pos.cashregisters.sort(function (obj1, obj2) {
                return obj1.journal.sequence - obj2.journal.sequence;
            });

            if (payment_pos) {
                var button = new module.MarcosPaypadButtonWidget(this, {
                    caption: "Enviar a caja",
                    action: function () {
                        //self.pos.logout_manager();
                        self.to_cashier();
                    }
                });

                button.appendTo(self.$el);

            } else {

                _.each(this.pos.cashregisters, function (cashregister) {

                    var button = new instance.point_of_sale.PaypadButtonWidget(self, {
                        pos: self.pos,
                        pos_widget: self.pos_widget,
                        cashregister: cashregister
                    });
                    button.appendTo(self.$el);
                });
            }

        },
        to_cashier: function () {
            var self = this;
            var currentOrder = self.pos.get('selectedOrder');
            if (currentOrder.get("client")) {
                self.send_to_cashier({action: "send_to_cashier"});
            } else {
                self.pos_widget.screen_selector.show_popup(
                    'marcos_input_popup_widget', {
                        message: "Introduzca un nombre que identifique al cliente para el cajero",
                        confirm: function () {
                            self.validate_before_send(this.$("#ref_name").val());
                        }

                    });

            }
        },
        validate_before_send: function (ref_name) {
            var self = this;
            if (ref_name.length > 0) {
                self.send_to_cashier({action: "send_to_cashier_with_ref_name", ref_name: ref_name});

            } else {
                self.to_cashier({})

            }
        },
        send_to_cashier: function (options) {
            var self = this;
            if (options.action === "send_to_cashier_with_ref_name") {
                self.pos_widget.payment_screen.validate_order({
                    action: "send_to_cashier_with_ref_name",
                    ref_name: options.ref_name
                });
            } else {
                self.pos_widget.payment_screen.validate_order({action: "send_to_cashier"});
            }

        }
    });

    module.OrderWidget = module.OrderWidget.extend({
        render_orderline: function (orderline) {
            var self = this;
            var el_str = openerp.qweb.render('Orderline', {widget: this, line: orderline});
            var el_node = document.createElement('div');
            el_node.innerHTML = _.str.trim(el_str);
            el_node = el_node.childNodes[0];
            el_node.orderline = orderline;
            el_node.addEventListener('click', this.line_click_handler);
            new instance.web.Model("stock.quant")
                .call("get_product_qty_in_location", [orderline.product.id, self.pos.shop.id])
                .then(function (result) {
                    _.each(result, function (item) {
                        if (item) {
                            $(el_node).find("li.info")
                                .append('<a class="product-available">(de <span>' + item[4] + '</span>)</a>')
                                .on("click", function () {
                                    self.showProductAvailablePop(orderline)
                                });
                        }
                    });
                })
                .fail(function(err, event){
                    event.preventDefault();
                });
            orderline.node = el_node;
            return el_node;
        },
        showProductAvailablePop: function (orderline) {
            var self = this;
            new instance.web.Model("stock.quant")
                .call("get_product_qty_by_location", [orderline.product.id])
                .then(function (result) {
                    var li_node = "";
                    _.each(result, function (li) {
                        li_node += "<li>" + li[1] + " -- " + li[4] + "</li><br/>"
                    });
                    self.pos_widget.screen_selector.show_popup('marcos_product_available_popup_widget', {
                        message: "Inventario por almacen",
                        location_qty: li_node
                    });

                })
                .fail(function(err, event){
                       event.preventDefault();
                        self.pos_widget.screen_selector.show_popup('error',{
                            'message':_t('Funcionalidad inactiva'),
                            'comment':_t('Es accion requiere conexion al servidor!.')
                        });
                });
        }
    });

    module.OrderButtonWidget = module.OrderButtonWidget.extend({
        selectOrder: function (event) {
            var self = this;
            //self.pos.logout_manager();
            this.pos.set({
                selectedOrder: this.order
            });

            if (self.order.get("type") === "refund") {
                this.pos.pos_widget.set_nc_mode(false);
            } else {
                var partner = this.order.get_client() ? this.order.get_client() : false;
                this.pos.pricelist_engine.update_products_ui(partner);
                this.pos.pos_widget.set_nc_mode(true);
            }
        },

    });

    module.PaypadButtonWidget = module.PosBaseWidget.extend({
        template: 'PaypadButtonWidget',
        init: function(parent, options){
            this._super(parent, options);
            this.cashregister = options.cashregister;
        },
        renderElement: function() {
            this._super();
            var self = this;

            this.$el.click(function(){
                //self.pos.logout_manager();
                if (self.pos.get('selectedOrder').get('screen') === 'receipt'){  //TODO Why ?
                    console.warn('TODO should not get there...?');
                    return;
                }
                self.pos.get('selectedOrder').addPaymentline(self.cashregister);
                self.pos_widget.screen_selector.set_current_screen('payment');
            });
        }
    });

        // this is used to notify the user if the pos is connected to the proxy
    module.ProxyStatusWidget = module.ProxyStatusWidget.extend({

        set_smart_status: function(status){
            if(status.status === 'connected'){
                var warning = false;
                var msg = ''
                if(this.pos.config.iface_scan_via_proxy){
                    var scanner = status.drivers.scanner ? status.drivers.scanner.status : false;
                    if( scanner != 'connected' && scanner != 'connecting'){
                        warning = true;
                        msg += _t('Scanner');
                    }
                }
                if (this.pos.config.ipf_odoo && this.pos.config.ipf_ip ){
                    var printer = status.status;
                    if( printer != 'connected' && printer != 'connecting'){
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Printer');
                    }
                }
                else if( this.pos.config.iface_print_via_proxy || this.pos.config.iface_cashdrawer ){
                    var printer = status.drivers.escpos ? status.drivers.escpos.status : false;
                    if( printer != 'connected' && printer != 'connecting'){
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Printer');
                    }
                }
                if( this.pos.config.iface_electronic_scale ){
                    var scale = status.drivers.scale ? status.drivers.scale.status : false;
                    if( scale != 'connected' && scale != 'connecting' ){
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Scale');
                    }
                }
                msg = msg ? msg + ' ' + _t('Offline') : msg;
                this.set_status(warning ? 'warning' : 'connected', msg);
            }else{
                //if (status.drivers.mess)
                this.set_status("warning", 'Impresora Desconectada');
            }
        }
    });

}
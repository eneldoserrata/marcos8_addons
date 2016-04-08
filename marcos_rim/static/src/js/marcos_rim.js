//function marcos_rim_widgets(instance) {
openerp.marcos_rim = function (instance, local) {
//    var module = instance.marcos_rim;
//    var _t = instance.web._t;
//    var QWeb = instance.web.qweb;

    var _t = openerp.web._t,
        _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;

    local.MobileWidget = instance.web.Widget.extend({
        start: function () {
            if (!$('#oe-mobilewidget-viewport').length) {
                $('head').append('<meta id="oe-mobilewidget-viewport" name="viewport" content="initial-scale=1.0; maximum-scale=1.0; user-scalable=0;">');
            }
            return this._super();
        },
        destroy: function () {
            $('#oe-mobilewidget-viewport').remove();
            return this._super();
        }
    });

    local.RimQcWidget = local.MobileWidget.extend({
        template: 'RinMainWidget',
        init: function (parent, params) {
            this._super(parent, params);
            var self = this;
            init_hash = $.bbq.getState();
            this.bacode_printer = null;
            this.barcode_scanner = new local.BarcodeScannerqc();
            this.sku_part_one = "U"
            this.sku_part_two = ""
            this.sku_part_tree = ""
            this.sku_part_four = ""
            this.sku_part_five = ""
            this.sku_part_six = ""
            this.serial_lot_id = 0;
            this.qcuserinfo = "X";
            this.qc_daily_qty = 0

        },
        renderElement: function () {
            var self = this;
            this._super();
            self.get_qc_user();
            self.get_daily_qc();
//            self.get_print_list();
//            self.logout()

        },
        load: function (picking_id) {
            var self = this;
        },
        start: function () {
            this._super();
            var self = this;
            instance.webclient.set_content_full_screen(true);
            self.barcode_scanner.connect(function (ean) {
                self.scan(ean);
            });
            self.$(".rim-button-search").click(function () {
                self.search_ui_btn();
            });
            self.$(".quality-btn").click(function () {
                self.set_quality(this);
            });
            self.$(".size-width-btn").click(function () {
                self.set_width(this);
            });
            self.$(".size-height-btn").click(function () {
                self.set_height(this);
            });
            self.$("#sku_trash").click(function () {
                self.trash_sku(this);
            });
            self.$("#send_print_btn").click(function () {
                self.print_send(this);
            });
            self.disable_buttons();
        },
        get_print_list: function () {
            var self = this;
            new instance.web.Model('marcos_rim.barcode_printer').query(['name', 'host', 'dir_path', 'users'], {context: new instance.web.CompoundContext()}).all().then(function (records) {
                _.each(records, function (record) {
                    var default_user_printer = -1;
                    if (record.users && self.bacode_printer === null) {
                        var printer_users = record.users.split(",");
                        var uid = self.session.uid.toString();
                        default_user_printer = $.inArray(uid, printer_users);
                        self.barcode_printer = default_user_printer;
                    }
                    ;

                    if (default_user_printer != -1) {
                        self.$("#js_printer_selector").append("<option value=" + record.id + " checked selected='selected'>" + record.name + "</option>");
                    } else {
                        self.$("#js_printer_selector").append("<option value=" + record.id + ">" + record.name + "</option>");
                    }
                    ;

                });
            });
        },
        print_send: function () {
            var self = this;
            var have_x = self.$(".skutext").text().indexOf("X");
            if (have_x === -1 && self.serial_lot_id != 0) {
                var skub = self.$(".skutext").text();
                return new instance.web.Model('stock.production.lot').call('make_qc', [self.serial_lot_id, skub, self.qcuserinfo], {context: new instance.web.CompoundContext()})
                    .then(function (action) {
                        if (action) {
                            self.trash_sku();
                            self.get_daily_qc();
                        } else if (action === false) {
                            return alert("La serie seleccionada no existe!, revise la goma nuevamente.");
                        }
                        ;
                    });
            }
            ;

        },
        formatVarString: function () {
            var args = [].slice.call(arguments);
            if (this.toString() != '[object Object]') {
                args.unshift(this.toString());
            }

            var pattern = new RegExp('{([1-' + args.length + '])}', 'g');
            return String(args[0]).replace(pattern, function (match, index) {
                return args[index];
            });
        },
        trash_sku: function () {
            var self = this;
            $(".skutext").html("");
            $("#serial_input").val("");
            self.sku_part_one = "U"
            self.sku_part_two = ""
            self.sku_part_tree = ""
            self.sku_part_four = ""
            self.sku_part_five = ""
            self.sku_part_six = ""
            self.serial_lot_id = 0;
            self.disable_buttons();
        },
        set_quality: function (value) {
            var self = this;
            if (self.sku_part_six != "") {
                self.sku_part_tree = self.$(value).text();
                self.show_sku();
            }
        },
        set_width: function (value) {
            var self = this;
            if (self.sku_part_six != "") {
                if (self.$(value).text() === "31/10.5") {
                    self.sku_part_four = "31";
                    self.sku_part_five = "10.5";
                    self.show_sku();
                } else {
                    self.sku_part_four = self.$(value).text();
                    self.show_sku();
                }
                ;

            }
            ;
        },
        set_height: function (value) {
            var self = this;
            if (self.sku_part_six != "") {
                self.sku_part_five = self.$(value).text();
                self.show_sku();
            }
        },
        scan: function (barcode) {
            var self = this
//            var isUser = barcode.length == 21 && barcode.substr(0, 6) == "QCUSER";
            var isTuid = barcode.length == 7;
//            if (isUser) {
//                if (self.qcuserinfo.barcode === barcode) {
//                    self.logout();
//                } else {
//                    self.get_qc_user(barcode);
//                };
//
//            } else
            if (isTuid && self.qcuserinfo != "X") {
                var lot_serial = $.trim(barcode.toUpperCase());
                self.$("#serial_input").val(lot_serial);
                self.search_lot(lot_serial);
            }
            ;
//            else {
//                self.qcuserinfo = "X";
//                return alert("Debe escanear su tarjeta de usuario para poder continuar");
//            };
        },
        get_daily_qc: function () {
            var self = this;
            return new instance.web.Model('stock.production.lot')
                .call("get_user_daily_process", [], {context: new instance.web.CompoundContext()})
                .then(function (result) {
                    self.show_daily_count(result);
                });

        },
        show_daily_count: function (qty) {
            var self = this;
            self.$("#qc_acceso").html("Acceso -- Gomas procesadas => " + qty);
        },
        get_qc_user: function () {
            var self = this
            return new instance.web.Model('marcos_rim.qc_users')
                .call("get_qc_user", [], {context: new instance.web.CompoundContext()})
                .then(function (record) {
                    if (record) {
                        self.qcuserinfo = record;
                        self.$("#qc_user_info_panel").html("Información SKU-B / " + self.qcuserinfo.name);
//                        self.$("#qc_panel").removeClass("panel_danger").addClass("panel-success");
//                        self.$("#send_print_btn").removeClass("btn-danger").addClass("btn-success");
                    }
//                    else {
//                        self.logout();
//                        return alert("Su tarjeta de usuario no es valida!");
//                    };

                });

        },
//        logout: function(){
//            self = this
//            self.$("#qc_user_info_panel").text("SKU-B Information / Debe escanear su usuario");
//            self.$("#qc_panel").removeClass("panel-success").addClass("panel_danger");
//            self.$("#send_print_btn").removeClass("btn-success").addClass("btn-danger");
//            self.qcuserinfo = "X";
//        },
        search_ui_btn: function () {
            var self = this;
            var serial_lot = self.$("#serial_input").val();
            self.search_lot(serial_lot);
        },
        search_lot: function (serial_lot) {
            var self = this;
            return new instance.web.Model('stock.production.lot').call('search_serial_lot_from_qc', [serial_lot], {context: new instance.web.CompoundContext()})
                .then(function (action) {
                    if (action) {
                        self.sku_format(action);
                    } else if (action === false) {
                        self.trash_sku();
                        return alert("Este TUID todavía no ha sido recibido!")
                    }
                });
        },
        sku_format: function (action) {
//            U-PLT-A-185-65-R14
            var self = this;
            var arr = action.sku.split("-");
            var len = arr.length;
            if (len === 3) {
                self.sku_part_one = "U";
                self.sku_part_two = arr[0];
                self.sku_part_tree = "X";
                self.sku_part_four = "X";
                self.sku_part_five = "X";
                self.sku_part_six = arr[2];
                self.enable_buttons();
            } else if (len === 6) {
                self.sku_part_one = arr[0];
                self.sku_part_two = arr[1];
                self.sku_part_tree = arr[2];
                self.sku_part_four = arr[3];
                self.sku_part_five = arr[4];
                self.sku_part_six = arr[5];
                if (self.qcuserinfo.canfix === true) {
                    self.enable_buttons();
                } else {
                    self.disable_buttons();
                }
                ;

            }
            ;
            self.serial_lot_id = action.id
            self.show_sku();
        },
        show_sku: function () {
            var self = this;
            var sku = self.formatVarString("{1}-{2}-{3}-{4}-{5}-{6}", self.sku_part_one,
                self.sku_part_two,
                self.sku_part_tree,
                self.sku_part_four,
                self.sku_part_five,
                self.sku_part_six);
            self.$(".skutext").html(sku);

        },
        disable_buttons: function () {
            var self = this;
            self.$(".quality-btn").prop("disabled", true);
            self.$(".size-width-btn").prop("disabled", true);
            self.$(".size-height-btn").prop("disabled", true);
        },
        enable_buttons: function () {
            var self = this;
            self.$(".quality-btn").prop("disabled", false);
            self.$(".size-width-btn").prop("disabled", false);
            self.$(".size-height-btn").prop("disabled", false);
        },
        quit: function () {
            this.destroy();
        },
        destroy: function () {
            this._super();
            // this.disconnect_numpad();
            this.barcode_scanner.disconnect();
            instance.webclient.set_content_full_screen(false);
        }
    });

    openerp.web.client_actions.add('marcosrim.ui', 'instance.marcos_rim.RimQcWidget');

    local.BarcodeScannerqc = instance.web.Class.extend({
        connect: function (callback) {
            var code = "";
            var timeStamp = 0;
            var timeout = null;

            this.handler = function (e) {
                if (e.which === 13) { //ignore returns
                    return;
                }

                if (timeStamp + 50 < new Date().getTime()) {
                    code = "";
                }

                timeStamp = new Date().getTime();
                clearTimeout(timeout);

                code += String.fromCharCode(e.which);

                timeout = setTimeout(function () {
                    if (code.length >= 2) {
                        callback(code);
                    }
                    code = "";
                }, 100);
            };

            $('body').on('keypress', this.handler);

        },
        disconnect: function () {
            $('body').off('keypress', this.handler);
        }
    });

///////////////////////////////////////////////////////////////////////////////////

    local.LocationMoveWidget = local.MobileWidget.extend({
        template: 'LocationMoveWidget',
        init: function (parent, params) {
            this._super(parent, params);
            var self = this;
            init_hash = $.bbq.getState();
            this.manual_box = init_hash.manual_box ? init_hash.manual_box : 0;
            this.barcode_scanner = new local.BarcodeScannerqc();
            this.lot_serial_or_location = null;
            this.sku_scan = [];
            this.location_id = null;

        },
        renderElement: function () {
            var self = this;
            this._super();
            self.$("#js_manual_box_transfer").on('click', function () {
                self.$("#modal-container-manual_box_transfer").modal("toggle");
            });
            self.$("modal-container-manual_box_transfer").on("shown.bs.modal", function () {
                self.barcode_scanner.disconnect();
                self.$("#tuid-textbox-location").val("").focus();
            });
            self.$("#modal-container-manual_box_transfer").on("hidden.bs.modal", function () {
                self.$("#tuid-textbox-location").val("").focus();
                self.$("#js_manual_box_transfer").blur();
                self.barcode_scanner.connect(function (ean) {
                    self.scan(ean);
                });
            });

//                self.$("#js_manual_box_transfer").hide();

        },
        load: function (picking_id) {
            var self = this;

        },
        start: function () {
            this._super();
            var self = this;
            instance.webclient.set_content_full_screen(true);
            self.barcode_scanner.connect(function (ean) {
                self.scan(ean);
            });
            self.$("#js_stock_move_clear").click(function () {
                self.clean_grid_row()
            });
            self.$("#js_stock_move").click(function () {
                self.move_from_to_location();
            });
            self.$("#search_from_box_transfer").click(function () {
                self.search_by_box();
            });
        },
        move_from_to_location: function () {
            var self = this;

            if (self.location_id === null) {
                alert("Debe seleccionar el lugar de destino");
                self.$("#to_location").text("Scan the row!");
                return false;
            } else {
                return new instance.web.Model("stock.production.lot")
                    .call("move_from_to_location", [self.sku_scan, self.location_id, new instance.web.CompoundContext()])
                    .then(function (result) {
                        if (result) {
                            self.clean_grid_row();
                            self.location_id = null;
                        } else {
                            alert("Ocurrio un problema en el servidor!");
                            self.location_id = null;
                            self.$("#to_location").text("Scan the row!");
                            return false
                        }
                        ;
                    });
            }
            ;
        },
        clean_grid_row: function () {
            var self = this;
            self.sku_scan = [];
            self.$("#detail_sku_to_move_table tr.sku_row").css("background-color", "#FF3700").fadeOut(100, function () {
                this.remove();
                self.$("#move_to").text("");
            });
            self.$("#move_count").text(0);

        },
        load_location: function (loc_barcode) {
            var self = this;
            return new instance.web.Model("stock.production.lot")
                .call("get_locations", [loc_barcode, context = new instance.web.CompoundContext()])
                .then(function (record) {
                    if (record) {
                        self.location_id = record.id;
                        self.$("#move_to").text(record.name);
                    } else {
                        return alert("La ubicación de almacen scaneada no es valída!")
                    }
                    ;
                });
        },
        search_by_box: function () {
            var self = this
            var lines = $("#tuid-textbox-location").val().split('\n');
            $.each(lines, function (key, val) {
                self.scan(val);
            });

        },
        scan: function (barcode) {
            var self = this;
            self.lot_serial_or_location = $.trim(barcode.toUpperCase());
            if (self.lot_serial_or_location.length < 7) {
                self.load_location(self.lot_serial_or_location);
            }
            else if (self.lot_serial_or_location.length === 7) {
                return new instance.web.Model("stock.production.lot")
                    .call("get_serial_to_move", [self.lot_serial_or_location])
                    .then(function (record) {
                        if (record) {
                            if (self.sku_scan.indexOf(record.serial) === -1) {
                                self.sku_scan.push(record.serial);
                                self.$("#detail_sku_to_move_table tr:first")
                                    .after("<tr class='sku_row' id='" + record.serial + "'" + "><td>" + record.serial + "</td><td>" + record.sku + "<td>" + record.source_location + "</td></tr>");
                                self.count_rows();
                            } else {
                                self.sku_scan = $.grep(self.sku_scan, function (value) {
                                    return value != record.serial
                                });

                                self.$('#detail_sku_to_move_table tr#' + record.serial).css("background-color", "#FF3700").fadeOut(400, function () {
                                    this.remove();
                                });
                            }
                            ;
                        } else {
                            alert("Este TUID: " + self.lot_serial_or_location + " ya fue vendido o no se encuentra en una ubicación interna");
                        }
                        ;
                    }).then(function () {
                        self.count_rows();
                    });
            }
            ;
        },
        count_rows: function () {
            self = this;
            var rowCount = $('#detail_sku_to_move_table tr').length - 1;
            self.$("#move_count").text(rowCount);
        }
    });

    openerp.web.client_actions.add('marcosrim.Locationmovewidget', 'instance.marcos_rim.LocationMoveWidget');

//////////////////////////////////Sale Picking//////////////////////////////////////////////////
    local.SalePickingWidget = local.MobileWidget.extend({
        template: 'SalePicking',
        init: function (parent, params) {
            this._super(parent, params);
            var self = this;
            init_hash = $.bbq.getState();
            this.picking_type_id = init_hash.picking_type_id ? init_hash.picking_type_id : 0;
            this.from_order = init_hash.from_order ? init_hash.from_order : false;
            this.order_name = init_hash.order_name ? init_hash.order_name : "";
            this.cliente = init_hash.cliente ? init_hash.cliente : "";
            this.order_id = init_hash.order_id ? init_hash.order_id : "";
            this.state = init_hash.state ? init_hash.state : "";

            this.barcode_scanner = new local.BarcodeScannerqc();
            this.tuids = [];
            this.skus = [];

            this.cp = 0;
            this.cg = 0;
            this.cs = 0;
            this.cb = 0;
            this.total = 0;

            this.id_price_to_change = null;
            this.price_to_change = null;

        },
        renderElement: function () {
            this._super();
            var self = this;
            self.$("#js_so").text(self.order_name);
            self.$("#js_cliente").text(self.cliente);
            self.$("#modal-container-29146").on("shown.bs.modal", function () {
                self.barcode_scanner.disconnect();
                self.$("#tuid-textbox").val("").focus();
            });
            self.$("#modal-container-29146").on("hidden.bs.modal", function () {
                self.$("#tuid-textbox").val("").focus();
                self.$("#modal-29146").blur();
                self.barcode_scanner.connect(function (ean) {
                    self.scan(ean);
                });
            });

            if (this.state === "draft" || this.state === "sent") {
                this.load()
            }
            ;
            self.$("#calc_price").click(function () {
                self.change_price();
            });

        },
        show_calc: function (selector) {
            var self = this;
            self.id_price_to_change = selector.id;
            self.sku_to_recalc = selector.id.replace("price-", "");
            self.price_to_change = self.$("#" + selector.id).html();
            self.$(".screen").html(self.price_to_change);
            self.$("#modal-container-calc").modal("toggle");
        },
        change_price: function () {
            var self = this;
            self.$(".eval").click();
            var new_price = parseFloat(self.$(".screen").html());
            if (new_price < 0) {
                return alert("No puede poner un precio negativo!");
            } else if (!$.isNumeric(new_price)) {
                return alert("A colocado un precio invalido!!");
            }
            ;
            $.each(self.skus, function (index, values) {
                if (self.skus[index].sku === self.sku_to_recalc) {
                    self.skus[index].values.precio = new_price
                    self.$("#" + self.id_price_to_change).html(self.$(".screen").html());
                    $("#" + self.sku_to_recalc + " .td_total").text(self.skus[index].values.tuid.length * self.skus[index].values.precio);
                }
            });
            self.calc_total();


        },
        calc_total: function () {
            var self = this;
            self.total = 0;
            $.each(self.skus, function (index, values) {
                self.total += self.skus[index].values.tuid.length * self.skus[index].values.precio;

            });
            self.count_rows();
        },
        load: function (picking_id) {
            var self = this;
            return new instance.web.Model("sale.order")
                .call("pull_scaned", [self.order_id, new instance.web.CompoundContext({"update_from_ui": true})])
                .then(function (result) {
                    if (result) {
                        self.add_tuid_from_order(result);
                    }
                    ;
                });

        },
        add_tuid_from_order: function (tuids) {
            var self = this
            $.each(tuids, function (index, value) {
                self.scan(value);
            });
        },
        start: function () {
            this._super();
            var self = this;
            instance.webclient.set_content_full_screen(true);
            self.barcode_scanner.connect(function (ean) {
                self.scan(ean);
            });
            self.$("#js_stock_move_clear").click(function () {
                self.clean_grid_row()
            });
            self.$("#js_stock_move").click(function () {
                self.move_from_to_location();
            });
            self.$("#search_from_box").click(function () {
                self.search_by_box();
            });
            self.$("#clean_order").click(function () {
                self.clean_grid_row();
            });
            self.$("#update_quotation").click(function () {
                self.update_quotation();
            });
        },
        update_quotation: function () {
            var self = this;

            return new instance.web.Model("sale.order")
                .call("update_from_ui", [self.order_id, self.skus, new instance.web.CompoundContext({"update_from_ui": true})])
                .then(function (result) {
                    if (result) {
                        self.clean_grid_row();
                        self.location_id = null;
                        window.history.back()
                    } else {
                        alert("Ocurrio un problema en el servidor!");
                        self.location_id = null;
                        return false
                    }
                    ;
                });

        },
        clean_grid_row: function () {
            var self = this;
            self.tuids = [];
            self.skus = [];
            self.cp = 0;
            self.cg = 0;
            self.cs = 0;
            self.cb = 0;
            self.total = 0;
            self.$("#sale_picking_table tr.sku_row").css("background-color", "#FF3700").fadeOut(100, function () {
                this.remove();
            });
            self.count_rows();

        },
        search_by_box: function () {
            var self = this
            var lines = $("#tuid-textbox").val().split('\n');
            $.each(lines, function (key, val) {
                self.scan(val);
            });

        },
        scan: function (barcode) {
            var self = this;
            self.lot_serial = $.trim(barcode.toUpperCase());


            if (self.lot_serial.length === 7) {
                new instance.web.Model("sale.order")
                    .call("get_serial_to_sale", [self.lot_serial, self.order_id])
                    .then(function (record) {
                        if (record) {
                            if (self.tuids.indexOf(record.tuid) === -1) {
                                self.tuids.push(record.tuid);
                                if (record.clasification === "p") {
                                    self.cp = self.cp + 1
                                } else if (record.clasification === "g") {
                                    self.cg = self.cg + 1
                                } else if (record.clasification === "s") {
                                    self.cs = self.cs + 1
                                } else if (record.clasification === "b") {
                                    self.cb = self.cb + 1
                                }
                                ;

                                var row = -1;
                                $.each(self.skus, function (index, values) {
                                    if (self.skus[index].sku === record.sku) {
                                        row = index;
                                        return
                                    }
                                });

                                if (row === -1) {
                                    self.skus.push({"sku": record.sku, "values": {  "product_id": record.product_id,
                                        "product_tmpl_id": record.product_tmpl_id,
                                        "cotizado": record.cotizado,
                                        "scaneado": 1,
                                        "precio": record.precio,
                                        "tuid": [record.tuid]}})
                                    self.$("#sale_picking_table tr:first")
                                        .after("<tr class='sku_row' id='" + record.sku + "'" + ">" +
                                            "<td class='td_sku'>" + record.sku + "</td>" +
                                            "<td class='td_cotizado'>" + record.cotizado + "</td>" +
                                            "<td class='td_scaneado'>" + 1 + "</td>" +
                                            "<td class='td_precio'><a class='btn' id='price-" + record.sku + "'>" + record.precio + "</a></td>" +
                                            "<td class='td_total'>" + record.precio + "</td>" +
                                            "<td class='td_tuid'><ol><li id='" + record.tuid + "'>" + record.tuid + "</li></ol></td>" +
                                            "</tr>");

                                    self.total += record.precio;
                                    self.$("#price-" + record.sku).on("click", function () {
                                        self.show_calc(this);
                                    });

                                } else {
                                    self.skus[row].values.tuid.push(record.tuid);
                                    self.skus[row].values.scaneado = self.skus[row].values.tuid.length;

                                    $("#" + record.sku + " .td_scaneado").text(self.skus[row].values.tuid.length);
                                    $("#" + record.sku + " .td_total").text(self.skus[row].values.tuid.length * record.precio);
                                    $("#" + record.sku + " .td_tuid").find("li").remove();

                                    $.each(self.skus[row].values.tuid, function (index, value) {
                                        $("#" + record.sku + " .td_tuid > ol").append("<li id='" + value + "'>" + value + "</li>")
                                    });

                                    self.total += record.precio;
                                }
                                ;
                                self.count_rows();

                            } else {
                                var skus_index = -1
                                self.tuids = _.without(self.tuids, record.tuid);
                                $.each(self.skus, function (index, values) {
                                    if (self.skus[index].sku === record.sku) {
                                        self.skus[index].values.tuid = _.without(self.skus[index].values.tuid, record.tuid)
                                        skus_index = index;
                                        self.total -= record.precio;
                                    }
                                });
                                self.skus[skus_index].values.scaneado = self.skus[skus_index].values.tuid.length;
                                $("#" + record.sku + " .td_scaneado").text(self.skus[skus_index].values.tuid.length);
                                $("#" + record.sku + " .td_total").text(self.skus[skus_index].values.tuid.length * record.precio);
                                self.$("#" + record.tuid).remove();
                                if (record.clasification === "p") {
                                    self.cp = self.cp - 1
                                } else if (record.clasification === "g") {
                                    self.cg = self.cg - 1
                                } else if (record.clasification === "s") {
                                    self.cs = self.cs - 1
                                } else if (record.clasification === "b") {
                                    self.cb = self.cb - 1
                                }
                                ;

                                self.count_rows();

                            }
                            ;
                        }
                        ;
                    });
            }
            ;

        },

        count_rows: function () {
            self = this;
            self.$("#rim_count").text(self.tuids.length);
            self.$("#js_cp").text(self.cp);
            self.$("#js_cg").text(self.cg);
            self.$("#js_cs").text(self.cs);
            self.$("#js_cb").text(self.cb);
            self.$("#js_to").text(self.total);
        }
    });

    openerp.web.client_actions.add('marcosrim.SalePickingWidget', 'instance.marcos_rim.SalePickingWidget');
////////////////////////////////////////////////////////////////////////////////////

    local.RimWebApp = instance.Widget.extend({
        template: "qc_and_transfer_template",
        init: function () {
            this._super();
        },
        start: function () {
        }
    });

    openerp.web.client_actions.add("marcos_rim.RimWebApp", "instance.marcos_rim.RimWebApp");

////////////////////////////////////////////////////////////////////////////////////

    instance.stock.PickingMainWidget = instance.stock.PickingMainWidget.extend({
        init: function (parent, params) {
            this._super(parent, params);
            var self = this;

        },

        drop_down: function () {
            var self = this;
            var barcode_printer_id = self.$("#js_printer_selector").val();
            var pack_op_ids = self.picking_editor.get_current_op_selection(true);
            if (pack_op_ids.length !== 0) {
                return new instance.web.Model('stock.pack.operation')
                    .call('action_drop_down', [pack_op_ids], {"context": new instance.web.CompoundContext({'barcode_printer_id': barcode_printer_id})})
                    .then(function () {
                        return self.refresh_ui(self.picking.id).then(function () {
                            if (self.picking_editor.check_done()) {
                                return self.done();
                            }
                        });
                    });
            }
        }

    });


    instance.stock.PickingEditorWidget = instance.stock.PickingEditorWidget.extend({
        init: function (parent, params) {
            this._super(parent, params);
            var self = this;
            this.bacode_printer = null;

        },
        renderElement: function () {
            var self = this;
            this._super();
            self.get_print_list();
        },
        get_print_list: function () {
            var self = this;
            new instance.web.Model('marcos_rim.barcode_printer').query(['name', 'host', 'dir_path', 'users']).all().then(function (records) {
                _.each(records, function (record) {
                    var default_user_printer = -1;
                    if (record.users && self.bacode_printer === null) {
                        var printer_users = record.users.split(",");
                        var uid = self.session.uid.toString();
                        default_user_printer = $.inArray(uid, printer_users);
                        self.barcode_printer = default_user_printer;
                    };
                    if (default_user_printer != -1) {
                        self.$("#js_printer_selector").append("<option value=" + record.id + " checked selected='selected'>" + record.name + "</option>");
                    } else {
                        self.$("#js_printer_selector").append("<option value=" + record.id + ">" + record.name + "</option>");
                    };
                });
            });
        }
    });


    local.SkuReport = local.MobileWidget.extend({
        template: 'SkuReportWidget',
        init: function (parent, params) {
            this._super(parent, params);
            var self = this;
            this.po_list = [];
            this.qualitya_summary = [];
            this.qualityb_summary = [];
            this.skua_summary = [];
            this.skub_summary = [];
            this.clasification = [];

        },
        renderElement: function () {
            var self = this;
            this._super();
            self.get_po();
            self.po_detail("all");
        },
        get_po: function () {
            var self = this;
            new instance.web.Model('marcos.rim.sku.report')
                .call('get_po', [], {"context": new instance.web.CompoundContext({})})
                .then(function (records) {

                    return self.$("#skus_grid").kendoGrid({
                        toolbar: ["excel"],
                        excel: {
                            fileName: "Kendo UI Grid Export.xlsx",
                            proxyURL: "http://demos.telerik.com/kendo-ui/service/export",
                            filterable: true
                        },
                        serverPaging: true,
                        dataSource: {
                            data: records,
                            schema: {
                                model: {
                                    fields: {
                                        po: { type: "string" },
                                        tuid: { type: "string" },
                                        skua: { type: "string" },
                                        costa: { type: "number" },
                                        qualitya: { type: "string" },
                                        skub: { type: "string" },
                                        costb: { type: "number" },
                                        qualityb: { type: "string" },
                                        clasification: { type: "string" },
                                        last_location: { type: "string" }
                                    }
                                }
                            },
                            pageSize: 100
                        },
                        sortable: true,
                        pageable: { refresh: true, pageSizes: [100, 500, 1000, 2000, 5000]},
                        groupable: true,
                        filterable: true,
                        columnMenu: true,
                        reorderable: true,
                        resizable: true,
                        selectable: "cell",
                        scrollable: true,
                        navigatable: true,
                        change: function () {
                            var selected = $.map(this.select(), function (item) {
                                return $(item).text();
                            });
                            self.pie_clear();
                            self.po_detail(selected);
                        },
                        columns: [
                            { field: "po", title: "PO", aggregates: ["count"], groupHeaderTemplate: "Count: #=count#" },
                            { field: "tuid", title: "TUID"},
                            { field: "skua", title: "SKU-A"},
                            { field: "costa", title: "Cost A", format: "{0:c}"},
                            { field: "qualitya", title: "Quality A"},

                            { field: "skub", title: "SKU-B"},
                            { field: "costb", title: "Cost-B", format: "{0:c}"},
                            { field: "qualityb", title: "Quality B"},
                            { field: "clasification", title: "Clasification"},
                            { field: "last_location", title: "Location"}
                        ]
                    });
                });
//                .then(function(grid){
//                    grid.bind("change", fucntion);
//                    console.log(self.$(".k-content"));
//                    self.$(".k-content").dblclick(self.cell_selected);
//                });
        },
        cell_selected: function () {
            var self = this;

//            var selected = $.map(this.select(), function(item) {
//                        return $(item).text();
//            });
//            console.log(self);
            console.log(self);
        },
        po_detail: function (selected) {
            var self = this;

            return new instance.web.Model('marcos.rim.sku.report')
                .call('get_report_summary', [selected], {"context": new instance.web.CompoundContext({})})
                .then(function (result) {
                    self.render_pie(result);
                });

        },
        pie_clear: function(){
            var self = this;
            self.qualitya_summary = [];
            self.qualityb_summary = [];
            self.skua_summary = [];
            self.skub_summary = [];
            self.clasification = [];

        },
        render_pie: function (result) {
            var self = this;
            self.graph_data_render(result);
            nv.addGraph(function () {
                var chart = nv.models.pieChart()
                    .x(function (d) {
                        return d.label
                    })
                    .y(function (d) {
                        return d.value
                    })
                    .showLabels(true);

                chart.pie.pieLabelsOutside(false).labelType("percent");

                d3.select("#chart_qualitya svg")
                    .datum(self.qualitya_summary)
                    .transition().duration(1200)
                    .call(chart);

                chart.dispatch.on('stateChange', function (e) {
                    nv.log('New State:', JSON.stringify(e));
                });

                return chart;
            });

            nv.addGraph(function () {
                var chart = nv.models.pieChart()
                    .x(function (d) {
                        return d.label
                    })
                    .y(function (d) {
                        return d.value
                    })
                    .showLabels(true);

                chart.pie.pieLabelsOutside(false).labelType("percent");

                d3.select("#chart_qualityb svg")
                    .datum(self.qualityb_summary)
                    .transition().duration(1200)
                    .call(chart);

                chart.dispatch.on('stateChange', function (e) {
                    nv.log('New State:', JSON.stringify(e));
                });

                return chart;
            });

            nv.addGraph(function () {
                var chart = nv.models.pieChart()
                    .x(function (d) {
                        return d.label
                    })
                    .y(function (d) {
                        return d.value
                    })
                    .showLabels(true)
                    .showLegend(false);

                chart.pie.pieLabelsOutside(false).labelType("percent");

                d3.select("#chart_skua svg")
                    .datum(self.skua_summary)
                    .transition().duration(1200)
                    .call(chart);

                chart.dispatch.on('stateChange', function (e) {
                    nv.log('New State:', JSON.stringify(e));
                });

                return chart;
            });

            nv.addGraph(function () {
                var chart = nv.models.pieChart()
                    .x(function (d) {
                        return d.label
                    })
                    .y(function (d) {
                        return d.value
                    })
                    .showLabels(true)
                    .showLegend(false);
                ;

                chart.pie.pieLabelsOutside(false).labelType("percent");

                d3.select("#chart_skub svg")
                    .datum(self.skub_summary)
                    .transition().duration(1200)
                    .call(chart);

                chart.dispatch.on('stateChange', function (e) {
                    nv.log('New State:', JSON.stringify(e));
                });

                return chart;
            });

            nv.addGraph(function () {
                var chart = nv.models.pieChart()
                    .x(function (d) {
                        return d.label
                    })
                    .y(function (d) {
                        return d.value
                    })
                    .showLabels(true)
                    .showLegend(true);
                ;

                chart.pie.pieLabelsOutside(false).labelType("percent");

                d3.select("#chart_clasification svg")
                    .datum(self.clasification)
                    .transition().duration(1200)
                    .call(chart);

                chart.dispatch.on('stateChange', function (e) {
                    nv.log('New State:', JSON.stringify(e));
                });

                return chart;
            });

        },
        graph_data_render: function (result) {
            var self = this;
            self.data_summary = []
            $.each(result.qualitya, function (key, value) {
                self.qualitya_summary.push({label: key, value: value});
            });

            $.each(result.qualityb, function (key, value) {
                self.qualityb_summary.push({label: key, value: value});
            });

            $.each(result.skua, function (key, value) {
                self.skua_summary.push({label: key, value: value});
            });

            $.each(result.skub, function (key, value) {
                self.skub_summary.push({label: key, value: value});
            });

            $.each(result.clasification, function (key, value) {
                self.clasification.push({label: key, value: value});
            });

        },
        collapseAll: function () {
            $("#skus_grid").find(".k-icon.k-collapse").trigger("click");
        },
        expandAll: function () {
            $("#skus_grid").find(".k-icon.k-expand").trigger("click");
        }
    });

    openerp.web.client_actions.add("marcos_rim.SkuReport", "instance.marcos_rim.SkuReport");


};




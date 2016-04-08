function marcos_pos_custom(instance, module) {

    module.MarcosTextAreaPopupWidget = instance.point_of_sale.PopUpWidget.extend({
        template: 'TextAreaPopupWidget',
        show: function (options) {
            var self = this;
            this._super();
            this.title = options.title || "";
            this.value = options.value || "";
            this.class = options.class || "";
            this.renderElement();

            self.$el.find("textarea").focus();

            this.$('.button.cancel').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.cancel) {
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.confirm) {
                    var note = self.$el.find("textarea").val();
                    options.confirm.call(note);
                }
            });
        }
    });

    module.MarcosInputPopupWidget = instance.point_of_sale.PopUpWidget.extend({
        template: 'MarcosInputPopupWidget',
        show: function (options) {
            var self = this;
            this._super();

            this.message = options.message || '';
            this.input_type = options.input_type || '';


            this.renderElement();

            this.$('.button.cancel').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.cancel) {
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.confirm) {
                    options.confirm.call(self);
                }
            });


            if (this.input_type === "pwd") {
                this.$("#ref_name").hide();
                this.$("#password").show();
                this.$("#password").focus();
            } else {
                this.$("#password").hide();
                this.$("#ref_name").show();
                this.$("#ref_name").focus();
            }

        }
    });

    module.MarcosProductAvailablePopupWidget = instance.point_of_sale.PopUpWidget.extend({
        template: 'MarcosProductAvailablePopupWidget',
        show: function (options) {
            var self = this;
            this._super();

            this.message = options.message || '';
            this.location_qty = options.location_qty || "";


            this.renderElement();

            this.$('.button.cancel').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.cancel) {
                    options.cancel.call(self);
                }
            });

            this.$('.button.confirm').click(function () {
                self.pos_widget.screen_selector.close_popup();
                if (options.confirm) {
                    options.confirm.call(self);
                }
            });
        }
    });

    module.MarcosHeaderButtonWidget = instance.point_of_sale.PosBaseWidget.extend({
        template: 'MarcosHeaderButtonWidget',
        init: function (parent, options) {
            options = options || {};
            this._super(parent, options);
            this.action = options.action;
            this.class = options.class;
        },
        renderElement: function () {
            var self = this;
            this._super();
            if (this.action) {
                this.$el.click(function () {
                    self.action();
                });
            }
        },
        show: function () {
            this.$el.removeClass('oe_hidden');
        },
        hide: function () {
            this.$el.addClass('oe_hidden');
        },
        lock: function () {
            this.$el.find("i").removeClass("fa-unlock");
            this.$el.find("i").addClass("fa-lock");
        },
        unlock: function () {
            this.$el.find("i").removeClass("fa-lock");
            this.$el.find("i").addClass("fa-unlock");
        }
    });

    module.MarcosPaypadButtonWidget = instance.point_of_sale.PosBaseWidget.extend({
        template: 'MarcosPaypadButtonWidget',
        init: function (parent, options) {
            options = options || {};
            this._super(parent, options);
            this.action = options.action;
            this.class = options.class;
            this.caption = options.caption;
        },
        renderElement: function () {
            var self = this;
            this._super();
            if (this.action) {

                this.$el.click(function () {
                    self.action();
                });
            }
        }
    });

    instance.web.View.include({
        //Override by Eneldo to prevent exception
        do_execute_action: function (action_data, dataset, record_id, on_closed) {
            var self = this;
            var result_handler = function () {
                if (on_closed) {
                    on_closed.apply(null, arguments);
                }
                if (self.getParent() && self.getParent().on_action_executed) {
                    return self.getParent().on_action_executed.apply(null, arguments);
                }
            };
            var context = new instance.web.CompoundContext(dataset.get_context(), action_data.context || {});

            // response handler
            var handler = function (action) {
                if (action && action.constructor == Object) {
                    // filter out context keys that are specific to the current action.
                    // Wrong default_* and search_default_* values will no give the expected result
                    // Wrong group_by values will simply fail and forbid rendering of the destination view
                    var ncontext = new instance.web.CompoundContext(
                        _.object(_.reject(_.pairs(dataset.get_context().eval()), function (pair) {
                            return pair[0].match('^(?:(?:default_|search_default_).+|.+_view_ref|group_by|group_by_no_leaf|active_id|active_ids)$') !== null;
                        }))
                    );
                    ncontext.add(action_data.context || {});
                    ncontext.add({active_model: dataset.model});
                    if (record_id) {
                        ncontext.add({
                            active_id: record_id,
                            active_ids: [record_id]
                        });
                    }
                    ncontext.add(action.context || {});
                    action.context = ncontext;
                    return self.do_action(action, {
                        on_close: result_handler
                    });
                } else {
                    self.do_action({"type": "ir.actions.act_window_close"});
                    return result_handler();
                }
            };

            if (action_data.special === 'cancel') {
                return handler({"type": "ir.actions.act_window_close"});
            } else if (action_data.type == "object") {
                var args = [[record_id]];
                if (action_data.args) {
                    try {
                        // Warning: quotes and double quotes problem due to json and xml clash
                        // Maybe we should force escaping in xml or do a better parse of the args array
                        var additional_args = JSON.parse(action_data.args.replace(/'/g, '"'));
                        args = args.concat(additional_args);
                    } catch (e) {
                        console.error("Could not JSON.parse arguments", action_data.args);
                    }
                }
                args.push(context);

                return dataset.call_button(action_data.name, args).then(handler)
                    .then(function () {
                        //Override by Eneldo to prevent exception when instance.webclient.menu.do_reload_needaction === undefined
                        try {
                            if (instance.webclient) {
                                instance.webclient.menu.do_reload_needaction();
                            }
                        } catch (err) {
                            console.error(err);
                        };

                    });
            } else if (action_data.type == "action") {
                return this.rpc('/web/action/load', {
                    action_id: action_data.name,
                    context: _.extend(instance.web.pyeval.eval('context', context), {
                        'active_model': dataset.model,
                        'active_ids': dataset.ids,
                        'active_id': record_id
                    }),
                    do_not_eval: true
                }).then(handler);
            } else {
                return dataset.exec_workflow(record_id, action_data.name).then(handler);
            }
        }
    });

}
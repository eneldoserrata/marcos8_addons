openerp.marcos_mail_button = function (instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;


    instance.web.ComposeMessageTopButton = instance.web.Widget.extend({
        template: 'ComposeMessageTopButton',

        start: function () {
            this.$('#oe_topbar_mailbutton_icon').on('click', this.on_compose_message);
            this._super();
        },

        on_compose_message: function (event) {
            var self = this;
            console.log(self)
            event.stopPropagation();
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'mail.compose.message',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {}
            };
            instance.client.action_manager.do_action(action);
        }
    });


    instance.web.UserMenu.include({
        do_update: function(){
            var self = this;
            this._super.apply(this, arguments);
            this.update_promise.then(function() {
                var mail_button = new instance.web.ComposeMessageTopButton();
                mail_button.appendTo(window.$('.oe_systray'));
            });
        }
    });


};
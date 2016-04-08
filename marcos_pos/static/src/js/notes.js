function marcos_pos_notes(instance, module) {

    var QWeb = instance.web.qweb;

    module.PosWidget.include({
        build_widgets: function () {
            var self = this;
            this._super();

            if (this.pos.config.iface_orderline_notes) {
                var linenote = $(QWeb.render('OrderlineNoteButton'));

                linenote.click(function () {
                    var line = self.pos.get('selectedOrder').getSelectedLine();
                    if (line) {
                        self.pos_widget.screen_selector.show_popup('marcos_textarea_popup_widget', {
                            title: _t('Agregar nota'),
                            value: line.get_note(),
                            class: line.cid,
                            confirm: function (note) {
                                line.set_note(" "+this);
                            }
                        });
                    }
                });

                linenote.appendTo(this.$('.control-buttons'));
                this.$('.control-buttons').removeClass('oe_hidden');
            }
        },
    });
}

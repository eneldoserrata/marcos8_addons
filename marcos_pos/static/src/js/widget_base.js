function marcos_pos_basewidget(instance, module){ //module is instance.point_of_sale

    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision

    // This is a base class for all Widgets in the POS. It exposes relevant data to the 
    // templates : 
    // - widget.currency : { symbol: '$' | '€' | ..., position: 'before' | 'after }
    // - widget.format_currency(amount) : this method returns a formatted string based on the
    //   symbol, the position, and the amount of money.
    // if the PoS is not fully loaded when you instanciate the widget, the currency might not
    // yet have been initialized. Use __build_currency_template() to recompute with correct values
    // before rendering.

    module.PosBaseWidget.include({

        format_number: function(amount,precision){
            var currency = (this.pos && this.pos.currency) ? this.pos.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
            var decimals = currency.decimals;

            if (precision && (typeof this.pos.dp[precision]) !== undefined) {
                decimals = this.pos.dp[precision];
            }

            if (typeof amount === 'number') {
                amount = round_di(amount,decimals).toFixed(decimals);
                amount = openerp.instances[this.session.name].web.format_value(round_di(amount, decimals), { type: 'float', digits: [69, decimals]});
            }


            return amount;

        }
    });

}

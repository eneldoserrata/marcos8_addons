openerp.marcos_pos = function (instance) {
    var module = instance.point_of_sale;
    marcos_pos_custom(instance, module);
    marcos_pos_widgets(instance, module);
    marcos_pos_db(instance, module);
    marcos_pos_device(instance, module);
    marcos_pos_models(instance, module);
    marcos_pos_basewidget(instance, module);
    marcos_pos_screens(instance, module);
    marcos_pos_notes(instance, module);

};

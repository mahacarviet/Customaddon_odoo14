odoo.define('mypet.bold', function (require) {
    "use strict";
    // import packages
    var basic_fields = require('web.basic_fields');
    var registry = require('web.field_registry');
    
    // widget implementation
    var BoldWidget = basic_fields.FieldChar.extend({
        _renderReadonly: function () {
            this._super();
            var old_html_render = this.$el.html();
            var new_html_render = '<b style="color:red;">' + old_html_render + '</b>'
            this.$el.html(new_html_render);
        },
    });
    
    registry.add('bold_red', BoldWidget); // add our "bold" widget to the widget registry
});

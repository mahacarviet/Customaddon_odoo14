odoo.define('sendo_integration.JsToCallWizard', function (require) {
"use strict";

let ListController = require('web.ListController');

let JsTocallWizard = ListController.include({
  renderButtons: function($node){
    this._super.apply(this, arguments);
    if (this.$buttons) {
      this.$buttons.on('click', '.o_button_to_call_wizard', this.sendo_seller_act_window.bind(this));
      this.$buttons.appendTo($node);
    }
  },
  action_to_call_wzard: function(event) {
    event.preventDefault();
    let self = this;
    self.do_action({
        name: "Open a wizard",
        type: 'ir.actions.act_window',
        res_model: 'sendo.connect.wizard',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
     });

  },
});
});
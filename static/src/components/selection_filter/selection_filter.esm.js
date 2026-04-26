import {Component} from "@odoo/owl";

export class SelectionFilter extends Component {
    static props = {
        data: [{
            id: {type: Number},
            name: {type: String},
            symbol: {type: Number, optional: true}
        }],
        label:String,
        onchange:Function,
    }

}

SelectionFilter.template = "sita_payment_integration.SelectionFilter";
import { Component } from "@odoo/owl";
export class Numcard extends Component{
    static props={
        total:String,
        title:String,
        amount:String,
        subtitle:String,


    }
}
 /*symbol:String,*/
Numcard.template="sita_payment_integration.Numcard";
import {Component, onWillStart, useState, useEnv, useEffect, onMounted} from "@odoo/owl";
import {registry} from "@web/core/registry";
import {SelectionFilter} from "./selection_filter/selection_filter.esm";
import {useService} from "@web/core/utils/hooks";
import {Numcard} from "./num_card/num_card.esm";
import {user} from "@web/core/user";


const months = [
    {number: 1, name: "January"},
    {number: 2, name: "February"},
    {number: 3, name: "March"},
    {number: 4, name: "April"},
    {number: 5, name: "May"},
    {number: 6, name: "June"},
    {number: 7, name: "July"},
    {number: 8, name: "August"},
    {number: 9, name: "September"},
    {number: 10, name: "October"},
    {number: 11, name: "November"},
    {number: 12, name: "December"},
];

export class Dashboard extends Component {
    setup() {

        this.currencyModel = 'res.currency';
        this.companyModel = 'res.company';
        this.transactionModel = 'transaction';
        this.orm = useService("orm");
        this.monthList = months;
        let currentYear = new Date().getFullYear();
        const startYear = currentYear - 6;
        console.log("Current User ID:", user);
        console.log("Current User ID:", user.userId);
        console.log("Current User Name:", user.name);

        this.yearList = []
        while (currentYear !== startYear) {
            this.yearList.push(currentYear);
            currentYear--;


        }
        // Access active companies


        this.companyService = useService("company");

        this.companyList = this.companyService.activeCompanyIds


        this.state = useState({
            currencyList: [{}],
            hotelList: [{}],
            totals: [],
            monthTotals: [],
            selectedCurrency: 0,
            selectedHotel: 0,
            selectedMonth: new Date().getMonth() + 1,
            selectedYear: new Date().getFullYear(),
            transactionMonthList: [],
            hotelsTransactionList: [],
            BarChartData: [],

        });

        onWillStart(async () => {
            await this._loadCurrency()
            await this._loadHotels()
            await this._loadTransactionTotals()


        });
        onMounted(this._renderGraph);
        useEffect(() => {
            this._renderGraph()
        }, () => [])
    }


    async _loadHotelTransactionList() {
        let domain = [];
        const currentYear = this.state.selectedYear;
        const currentMonth = this.state.selectedMonth;
        let startDatetime = new Date(currentYear, currentMonth - 1, 1, 0, 0, 0)
        let endDatetime = new Date(currentYear, currentMonth, 0, 23, 59, 59)

        console.log("this.state.selectedHotel", this.state.selectedHotel)

        if (parseInt(this.state.selectedHotel) === 0) {
            this.state.hotelsTransactionList = [['Hotel', 'L.E', '$',],]
            for (let i = 0; i < this.state.hotelList.length; i++) {
                domain = []
                domain.push(['verified_on', '>=', startDatetime], ["verified_on", '<=', endDatetime], ["state", '=', "done"])
                domain.push(["company_id", '=', parseInt(this.state.hotelList[i].id)])
                let data_range_totals = await this.orm.call(this.transactionModel, "read_group", [
                    domain,
                    ["amount", "currency_id"],
                    ["currency_id", "amount:sum"]

                ]);


                if (parseInt(this.state.selectedCurrency) === 0) {
                    this.state.hotelsTransactionList.push([
                            this.state.hotelList[i].name,
                            data_range_totals.length >= 1 ? data_range_totals[0].amount : 0,
                            data_range_totals.length >= 2 ? data_range_totals[1].amount : 0,
                        ]
                    )

                } else if (parseInt(this.state.selectedCurrency) === 2) {//USD
                    this.state.hotelsTransactionList.push([
                            this.state.hotelList[i].name,
                            0,
                            data_range_totals.length >= 1 ? data_range_totals[0].amount : 0,
                        ]
                    )

                } else {
                    this.state.hotelsTransactionList.push([
                        this.state.hotelList[i].name,

                        data_range_totals.length >= 1 ? data_range_totals[0].amount : 0,

                        0]
                    )
                }


            }


        } else {

            this.state.hotelsTransactionList = [['Hotel', 'L.E', '$',], ["", 0, 0]]

        }

    }

    async _loadAllTransactionData() {
        this.state.transactionMonthList = [];
        const currentMonth = this.state.selectedMonth;
        const currentYear = this.state.selectedYear;
        for (let i = 0; i < 12; i++) {

            let startDate = new Date(currentYear, currentMonth - i - 1, 1)
            let endDate = new Date(currentYear, currentMonth - i, 0)
            let startDatetime = new Date(currentYear, currentMonth - i - 1, 1, 0, 0, 0)
            let endDatetime = new Date(currentYear, currentMonth - i, 0, 23, 59, 59)
            let domain = []

            if (this.state.selectedHotel > 0) {
                domain.push(["state", '=', "done"])
                domain.push(["company_id", '=', parseInt(this.state.selectedHotel)])
            } else {
                domain.push(["state", '=', "done"], ["company_id", 'in', this.companyList])
            }
            if (this.state.selectedCurrency > 0) {
                domain.push(["currency_id", '=', parseInt(this.state.selectedCurrency)])
            }
            domain.push(['verified_on', '>=', startDatetime], ["verified_on", '<=', endDatetime])


            let data_range_totals = await this.orm.call(this.transactionModel, "read_group", [
                domain,
                ["amount", "currency_id"],
                ["currency_id", "amount:sum"]

            ]);


            if (parseInt(this.state.selectedCurrency) === 0)

                this.state.transactionMonthList.push(
                    {
                        name: startDate.toLocaleString('default', {month: 'long'}) + " " + startDate.getFullYear(),
                        EGP: data_range_totals.length >= 1 ? data_range_totals[0].amount : 0,
                        USD: data_range_totals.length >= 2 ? data_range_totals[1].amount : 0,
                    })
            else if (parseInt(this.state.selectedCurrency) === 2) {//USD{
                this.state.transactionMonthList.push(
                    {
                        name: startDate.toLocaleString('default', {month: 'long'}) + " " + startDate.getFullYear(),
                        EGP: 0,
                        USD: data_range_totals.length >= 1 ? data_range_totals[0].amount : 0,
                    })
            } else {
                this.state.transactionMonthList.push(
                    {
                        name: startDate.toLocaleString('default', {month: 'long'}) + " " + startDate.getFullYear(),
                        EGP: data_range_totals.length >= 1 ? data_range_totals[0].amount : 0,
                        USD: 0,
                    })
            }


        }


        this.state.BarChartData = [['Year', 'L.E', '$',],];
        for (let i = 0; i < this.state.transactionMonthList.length; i++) {

            this.state.BarChartData.push([this.state.transactionMonthList[i].name, this.state.transactionMonthList[i].EGP, this.state.transactionMonthList[i].USD])
        }
        console.log("BarChartDataData", this.state.BarChartDataData)

    }


    async _renderGraph() {
        google.charts.load('current', {'packages': ['bar', 'line']});
        await this._loadAllTransactionData();
        await this._loadHotelTransactionList();
        const allData = this.state.BarChartData;
        const hotelData = this.state.hotelsTransactionList;
        console.log("hotelData", hotelData)
        google.charts.setOnLoadCallback(drawChart);


        function drawChart() {
            if (allData) {

                var data = google.visualization.arrayToDataTable([

                    ...allData

                ]);


                let options = {
                    chart: {
                        title: 'Success Transaction Last 12 Month',
                        subtitle: '',
                    },
                    titleTextStyle: {
                        color: '#1E88E5',      // Title color
                        fontSize: 20,          // Title font size
                        bold: true,            // Bold text
                        italic: false,         // Italic text
                        fontName: 'Poppins'    // Custom font
                    },
                    subtitleTextStyle: {
                        color: '#757575',      // Subtitle color
                        fontSize: 14,          // Subtitle font size
                        bold: false,
                        italic: true,
                        fontName: 'Poppins'
                    },
                    // hAxis: {
                    //     title: 'Months',
                    //     titleTextStyle: {
                    //         color: '#1E88E5',
                    //         fontSize: 16,
                    //         bold: true,
                    //         italic: false,
                    //         fontName: 'Poppins'
                    //     },
                    // },
                     axes: {
                         x: {
                             0: {
                                 side: 'bottom',
                                 label: 'Months',
                                 textStyle: {color: '#093360', fontSize: 12, fontName: 'Poppins'}
                             }
                         },
                         y: {
                             0: {
                                 label: 'Sales (EGP)',
                                 textStyle: {color: '#093360', fontSize: 12}
                             }
                         }
                     },

                    colors: ['#8E24AA', '#039BE5', '#FDD835'],
                    width: '100%',
                    height: '100%',

                    bars: 'vertical' // Required for Material Bar Charts.
                };

                let chart = new google.charts.Bar(document.getElementById('barchart_material'));

                chart.draw(data, google.charts.Bar.convertOptions(options));
            }

            if (hotelData.length) {
                let data = google.visualization.arrayToDataTable([

                    ...hotelData

                ]);
                let options = {
                    chart: {
                        title: 'Hotels Sales Comparison ',
                        subtitle: '',
                    },
                    titleTextStyle: {
                        color: '#1E88E5',      // Title color
                        fontSize: 20,          // Title font size
                        bold: true,            // Bold text
                        italic: false,         // Italic text
                        fontName: 'Poppins'    // Custom font
                    },
                    subtitleTextStyle: {
                        color: '#757575',      // Subtitle color
                        fontSize: 14,          // Subtitle font size
                        bold: false,
                        italic: true,
                        fontName: 'Poppins'
                    },
                    hAxis: {
                        title: 'Months',
                        titleTextStyle: {
                            color: '#1E88E5',
                            fontSize: 16,
                            bold: true,
                            italic: false,
                            fontName: 'Poppins'
                        },
                        textStyle: {
                            color: '#093360',
                            fontSize: 13,
                            bold: false,
                            italic: true,
                            fontName: 'Poppins'
                        },
                        slantedText: true,      // make labels diagonal if long
                        slantedTextAngle: 45,   // rotation angle
                    },

                    colors: ['#8E24AA', '#039BE5', '#FDD835'],
                    width: '100%',
                    height: '100%'

                };

                var chart = new google.charts.Line(document.getElementById('compare_line_chart'));

                chart.draw(data, google.charts.Line.convertOptions(options));
            }


        }
    }

    async onChangeYear(e) {
        this.state.selectedYear = parseInt(e.target.value);
        await this._loadTransactionTotals();
        await this._loadHotelTransactionList();
        await this._renderGraph()
    }

    async onChangeMonth(e) {
        this.state.selectedMonth = parseInt(e.target.value)
        await this._loadTransactionTotals();
        await this._loadHotelTransactionList();
        await this._renderGraph();

    }

    async _onchangeCurrency(e) {
        console.log("e in onchange Currency", e.target.value);
        this.state.selectedCurrency = e.target.value;
        await this._loadTransactionTotals();
        await this._loadHotelTransactionList();
        await this._renderGraph()

    }

    async _onchangeHotel(e) {
        console.log("e in onchange Hotel", e.target.value);
        this.state.selectedHotel = e.target.value;
        await this._loadTransactionTotals();
        await this._loadHotelTransactionList();
        await this._renderGraph();
    }

    async _loadCurrency() {
        this.state.currencyList = await this.orm.searchRead(this.currencyModel, [], ["id", "name", "symbol",])
    }

    async _loadHotels() {
        this.state.hotelList = await this.orm.searchRead(this.companyModel, [
            ["id", 'in', this.companyList]
        ], ['name'])


    }

    async _loadTransactionTotals(domain = []) {


        if (this.state.selectedHotel > 0) {
            domain.push(["state", '=', "done"])
            domain.push(["company_id", '=', parseInt(this.state.selectedHotel)])
        } else {
            domain.push(["state", '=', "done"], ["company_id", 'in', this.companyList])
        }
        if (this.state.selectedCurrency > 0) {
            domain.push(["currency_id", '=', parseInt(this.state.selectedCurrency)])
        }

        this.state.totals = await this.orm.call(this.transactionModel, "read_group", [
            domain,
            ["amount", "currency_id"],
            ["currency_id", "amount:sum"]
        ]);
        const currentMonth = this.state.selectedMonth;
        const currentYear = this.state.selectedYear;
        let startDatetime = new Date(currentYear, currentMonth - 1, 1, 0, 0, 0)
        let endDatetime = new Date(currentYear, currentMonth, 0, 23, 59, 59)
        domain.push(['verified_on', '>=', startDatetime], ["verified_on", '<=', endDatetime])
        this.state.monthTotals = await this.orm.call(this.transactionModel, "read_group", [
            domain,
            ["amount", "currency_id"],
            ["currency_id", "amount:sum"]
        ]);
        console.log("monthTotals", this.state.monthTotals)
    }


}

Dashboard.template = "sita_payment_integration.Dashboard";
Dashboard.components = {SelectionFilter, Numcard};
registry.category("actions").add("sita_payment_integration.Dashboard", Dashboard)
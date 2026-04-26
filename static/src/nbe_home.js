function errorCallback(error) {
    console.log(JSON.stringify(error));
}

function cancelCallback() {
    console.log('Payment cancelled');
}

function completeCallback() {
    alert('Completed the payment');
    window.location.href = "/receipt page";
    <!--                retrieveOrder();-->


}

// function retrieveOrder() {
//     const Http = new XMLHttpRequest();
//     var merchant = 'TESTEGPTEST';
//     var order_id = {
//     {
//         context['order_id']
//     }
// }
//     ;var url = "https://test-nbe.gateway.mastercard.com/api/rest/version/65/merchant/".concat(merchant, "/order/", orderid);
//     alert('url is :', url);
//     Http.open("GET", url);
//     Http.send();
//
//     Http.onreadystatechange = (e) => {
//         alert(Http.responseText);
//
//
//     }
//
//
// }

Checkout.configure({
    // console.log('in checkout conifutre')
    session: {
        id: session_id, version: 'session_version'
    }, order: {
        description: 'Ordered goods', id: 'order_id',
    }, interaction: {
        operation: 'PURCHASE',

        merchant: {
            name: 'NBE Test', address: {
                line1: '200 Sample St', line2: '1234 Example Town'
            }, email: 'catherine@sita-eg.com'
        }
    },
});
console.log('session', session_id);
Checkout.configure({
                    session: {
                    id: '<t t-esc="session_id"/>',
                    version: '<t t-esc="session_version"/>',
                    },
                    order: {
                    description: '<t t-esc="description"/>',
                    id: '<t t-esc="order_id"/>',
                    },
                    interaction: {
                    operation: 'PURCHASE',
                    merchant: {
                    name: '<t t-esc="merchant_name"/>'
                    },
                    },

                    });
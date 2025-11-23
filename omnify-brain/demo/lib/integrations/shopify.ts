import axios from 'axios';
import { format, startOfDay, endOfDay } from 'date-fns';

export interface ShopifyOrder {
    id: number;
    created_at: string;
    total_price: string;
    customer: {
        id: number;
        email: string;
    };
    line_items: Array<{
        product_id: number;
        quantity: number;
        price: string;
    }>;
}

export interface ShopifyCustomer {
    id: number;
    email: string;
    total_spent: string;
    orders_count: number;
    created_at: string;
}

export class ShopifyClient {
    private storeUrl: string;
    private accessToken: string;
    private baseUrl: string;

    constructor(storeUrl: string, accessToken: string) {
        this.storeUrl = storeUrl;
        this.accessToken = accessToken;
        this.baseUrl = `https://${storeUrl}/admin/api/2024-01`;
    }

    /**
     * Fetch orders for a date range
     */
    async fetchOrders(dateRange: { start: Date; end: Date }) {
        const url = `${this.baseUrl}/orders.json`;
        const orders: ShopifyOrder[] = [];
        let hasMore = true;
        let pageInfo: string | null = null;

        try {
            while (hasMore) {
                const params: any = {
                    status: 'any',
                    created_at_min: startOfDay(dateRange.start).toISOString(),
                    created_at_max: endOfDay(dateRange.end).toISOString(),
                    limit: 250
                };

                if (pageInfo) {
                    params.page_info = pageInfo;
                }

                const response = await axios.get(url, {
                    headers: {
                        'X-Shopify-Access-Token': this.accessToken
                    },
                    params
                });

                orders.push(...response.data.orders);

                // Check for pagination
                const linkHeader = response.headers.link;
                if (linkHeader && linkHeader.includes('rel="next"')) {
                    const match = linkHeader.match(/<[^>]*page_info=([^&>]+)[^>]*>;\s*rel="next"/);
                    pageInfo = match ? match[1] : null;
                } else {
                    hasMore = false;
                }
            }

            return orders;
        } catch (error: any) {
            console.error('[SHOPIFY] Error fetching orders:', error.response?.data || error.message);
            throw new Error(`Shopify API Error: ${error.response?.data?.errors || error.message}`);
        }
    }

    /**
     * Fetch customer data for LTV calculation
     */
    async fetchCustomers(limit: number = 250) {
        const url = `${this.baseUrl}/customers.json`;

        try {
            const response = await axios.get(url, {
                headers: {
                    'X-Shopify-Access-Token': this.accessToken
                },
                params: {
                    limit
                }
            });

            return response.data.customers as ShopifyCustomer[];
        } catch (error: any) {
            console.error('[SHOPIFY] Error fetching customers:', error.response?.data || error.message);
            throw new Error(`Shopify API Error: ${error.response?.data?.errors || error.message}`);
        }
    }

    /**
     * Calculate daily revenue from orders
     */
    calculateDailyRevenue(orders: ShopifyOrder[]): Map<string, number> {
        const dailyRevenue = new Map<string, number>();

        for (const order of orders) {
            const date = format(new Date(order.created_at), 'yyyy-MM-dd');
            const revenue = parseFloat(order.total_price);

            dailyRevenue.set(date, (dailyRevenue.get(date) || 0) + revenue);
        }

        return dailyRevenue;
    }

    /**
     * Calculate average LTV
     */
    calculateAverageLTV(customers: ShopifyCustomer[]): number {
        if (customers.length === 0) return 0;

        const totalLTV = customers.reduce((sum, customer) => {
            return sum + parseFloat(customer.total_spent);
        }, 0);

        return totalLTV / customers.length;
    }
}

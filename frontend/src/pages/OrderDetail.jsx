import { useQuery } from "@tanstack/react-query";
import { Link, useLocation, useParams } from "react-router-dom";

import { getOrder } from "../api";
import { Address, LineItems, Totals } from "../components/OrderParts";
import { Alert, Loading, PageError } from "../components/Status";
import { formatDate } from "../utils";

export default function OrderDetail() {
  const { id } = useParams();
  const { state } = useLocation();
  const { data: order, isPending, error } = useQuery({ queryKey: ["orders", id], queryFn: () => getOrder(id) });

  if (isPending) return <Loading />;
  if (error) return <PageError error={error} what="order" />;

  return (
    <div className="container mx-auto max-w-4xl px-4 py-8">
      {state?.justPlaced && <div className="mb-6"><Alert tone="success">Thank you! Your order has been placed.</Alert></div>}
      <div className="mb-6 flex flex-wrap items-baseline justify-between gap-2">
        <h1 className="text-3xl font-bold">Order #{order.number}</h1>
        <p className="text-gray-600">Placed {formatDate(order.created_at, { dateStyle: "long", timeStyle: "short" })}</p>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 md:grid-cols-3">
        <section className="card"><h2 className="mb-2 font-semibold">Billing</h2><Address address={order.billing_address} /></section>
        <section className="card"><h2 className="mb-2 font-semibold">Shipping</h2><Address address={order.shipping_address} province={order.province_name} /></section>
        <section className="card">
          <h2 className="mb-2 font-semibold">Payment</h2>
          <p className="text-gray-700">{order.cardholder_name}<br />Card ending in {order.card_last4}</p>
        </section>
      </div>

      <section className="card">
        <h2 className="mb-2 font-semibold">Items</h2>
        <LineItems items={order.items} />
        <div className="border-t border-gray-200 pt-4 md:ml-auto md:w-1/2">
          <Totals totals={order} />
        </div>
      </section>

      <div className="mt-6 flex gap-4">
        <Link to="/products" className="btn-primary">Continue shopping</Link>
        <Link to="/account" className="btn-secondary">View all orders</Link>
      </div>
    </div>
  );
}

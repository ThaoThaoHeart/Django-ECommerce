import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getOrders } from "../api";
import { Loading } from "../components/Status";
import { useAuth } from "../hooks/useAuth";
import { formatDate, formatMoney } from "../utils";

export default function Account() {
  const { user } = useAuth();
  const orders = useQuery({ queryKey: ["orders"], queryFn: getOrders });

  return (
    <div className="container mx-auto max-w-4xl space-y-6 px-4 py-8">
      <h1 className="text-3xl font-bold">My Account</h1>

      <section className="card">
        <h2 className="mb-4 text-xl font-semibold">Account information</h2>
        <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div><dt className="text-sm text-gray-600">Email</dt><dd className="font-medium">{user.email}</dd></div>
          <div><dt className="text-sm text-gray-600">Member since</dt><dd className="font-medium">{formatDate(user.date_joined, { dateStyle: "long" })}</dd></div>
        </dl>
      </section>

      <section className="card">
        <h2 className="mb-4 text-xl font-semibold">Order history</h2>
        {orders.isPending ? (
          <Loading />
        ) : orders.data?.length ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-gray-200 text-gray-600">
                <tr><th className="py-2 pr-4">Order</th><th className="py-2 pr-4">Date</th><th className="py-2 pr-4">Items</th><th className="py-2 text-right">Total</th></tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {orders.data.map((order) => (
                  <tr key={order.id}>
                    <td className="py-3 pr-4"><Link to={`/orders/${order.id}`} className="link font-medium">#{order.number}</Link></td>
                    <td className="py-3 pr-4">{formatDate(order.created_at)}</td>
                    <td className="py-3 pr-4">{order.item_count}</td>
                    <td className="py-3 text-right font-medium">{formatMoney(order.total)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <>
            <p className="text-gray-600">You haven't placed any orders yet.</p>
            <Link to="/products" className="btn-primary mt-4 py-2">Start shopping</Link>
          </>
        )}
      </section>
    </div>
  );
}

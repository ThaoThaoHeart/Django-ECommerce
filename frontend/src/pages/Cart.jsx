import { Link } from "react-router-dom";

import { errorsOf, removeCartItem, updateCartItem } from "../api";
import { Totals } from "../components/OrderParts";
import ProductImage from "../components/ProductImage";
import { Alert, Loading } from "../components/Status";
import { useCart, useCartMutation } from "../hooks/useCart";
import { formatMoney, pluralize } from "../utils";

export default function Cart() {
  const { data: cart, isPending } = useCart();
  const update = useCartMutation(({ id, quantity }) => updateCartItem(id, quantity));
  const remove = useCartMutation(removeCartItem);
  const busy = update.isPending || remove.isPending;
  const failure = update.error ?? remove.error;

  if (isPending) return <Loading />;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold">Your Cart</h1>
      {failure && <div className="mb-4"><Alert>{Object.values(errorsOf(failure)).flat().join(" ")}</Alert></div>}

      {cart.items.length === 0 ? (
        <div className="card p-10 text-center">
          <p className="mb-4 text-xl text-gray-700">Your cart is empty.</p>
          <Link to="/products" className="btn-primary">Browse Products</Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-3">
          <ul className={`divide-y divide-gray-200 rounded-lg bg-white shadow-md lg:col-span-2 ${busy ? "opacity-60" : ""}`}>
            {cart.items.map((item) => (
              <li key={item.id} className="flex flex-col gap-4 p-4 sm:flex-row sm:items-center md:p-6">
                <div className="hidden h-20 w-20 shrink-0 sm:block">{item.product && <ProductImage product={item.product} />}</div>
                <div className="flex-1">
                  <h2 className="text-lg font-semibold">
                    {item.product ? <Link to={`/products/${item.product.slug}`} className="hover:text-red-600">{item.product_title}</Link> : item.product_title}
                  </h2>
                  {item.selected_variations && <p className="text-sm text-gray-600">{item.selected_variations}</p>}
                  {item.product && <p className="text-sm text-gray-600">{formatMoney(item.unit_price)} each</p>}
                  {item.error && <p className="mt-1 text-sm font-medium text-red-600">{item.error}</p>}
                </div>

                <div className="flex items-center gap-2">
                  <div className="flex items-center rounded-lg border border-gray-300 bg-white">
                    <button type="button" disabled={busy} aria-label="Decrease quantity" className="rounded-l-lg px-3 py-2 hover:bg-gray-100"
                      onClick={() => update.mutate({ id: item.id, quantity: item.quantity - 1 })}>&minus;</button>
                    <span className="w-10 text-center" aria-label="Quantity">{item.quantity}</span>
                    <button type="button" aria-label="Increase quantity" className="rounded-r-lg px-3 py-2 hover:bg-gray-100 disabled:opacity-40"
                      disabled={busy || !item.product || item.quantity >= item.product.stock}
                      onClick={() => update.mutate({ id: item.id, quantity: item.quantity + 1 })}>+</button>
                  </div>
                  <button type="button" disabled={busy} className="px-3 py-2 text-sm text-gray-600 hover:text-red-600" onClick={() => remove.mutate(item.id)}>
                    Remove
                  </button>
                </div>

                <p className="font-semibold sm:w-24 sm:text-right">{formatMoney(item.line_total)}</p>
              </li>
            ))}
          </ul>

          <aside className="card">
            <h2 className="mb-4 text-lg font-semibold">Summary</h2>
            <p className="mb-2 text-sm text-gray-600">{pluralize(cart.item_count, "item")}</p>
            <Totals totals={cart} showTax={false} />
            {cart.has_errors ? (
              <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">Please fix the highlighted items before checking out.</p>
            ) : (
              <Link to="/checkout" className="btn-primary mt-4 block w-full">Checkout</Link>
            )}
            <Link to="/products" className="link mt-3 block text-center text-sm">Continue shopping</Link>
          </aside>
        </div>
      )}
    </div>
  );
}

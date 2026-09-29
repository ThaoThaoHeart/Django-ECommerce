import { formatMoney } from "../utils";

/** Pieces shared by the checkout summary and the order page; they accept a cart summary or an order. */

export function LineItems({ items }) {
  return (
    <ul className="divide-y divide-gray-200">
      {items.map((item) => (
        <li key={item.id} className="flex justify-between gap-4 py-3 text-sm">
          <div>
            <p className="font-medium text-gray-900">
              {item.product_title} <span className="text-gray-500">&times; {item.quantity}</span>
            </p>
            {item.selected_variations && <p className="text-gray-500">{item.selected_variations}</p>}
          </div>
          <p className="whitespace-nowrap font-medium">{formatMoney(item.line_total)}</p>
        </li>
      ))}
    </ul>
  );
}

export function Totals({ totals, showTax = true }) {
  const row = "flex justify-between";
  return (
    <>
      <dl className="space-y-2 text-sm">
        <div className={row}><dt className="text-gray-600">Subtotal</dt><dd>{formatMoney(totals.subtotal)}</dd></div>
        {showTax && (
          <>
            <div className={row}><dt className="text-gray-600">Tax</dt><dd>{formatMoney(totals.tax)}</dd></div>
            <div className={row}>
              <dt className="text-gray-600">Shipping</dt>
              <dd>{Number(totals.shipping_cost) ? formatMoney(totals.shipping_cost) : "Free"}</dd>
            </div>
            <div className={`${row} border-t border-gray-200 pt-2 text-base font-semibold`}><dt>Total</dt><dd>{formatMoney(totals.total)}</dd></div>
          </>
        )}
      </dl>
      {!showTax && <p className="mt-2 text-xs text-gray-500">Tax and shipping are calculated at checkout.</p>}
    </>
  );
}

export function Address({ address, province }) {
  return (
    <address className="not-italic text-gray-700">
      {address.full_name}<br />
      {address.address_line_1}<br />
      {address.address_line_2 && <>{address.address_line_2}<br /></>}
      {address.city}{province && `, ${province}`} {address.postal_code}<br />
      Canada
    </address>
  );
}

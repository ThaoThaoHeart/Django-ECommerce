import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, Navigate, useNavigate } from "react-router-dom";

import { errorsOf, getProvinces, placeOrder, validateCheckout } from "../api";
import { Field, FieldErrors, FieldGroup } from "../components/Field";
import { Address, LineItems, Totals } from "../components/OrderParts";
import { Alert, Loading } from "../components/Status";
import { useCart } from "../hooks/useCart";
import { formatMoney } from "../utils";

const STEPS = [
  { label: "Shipping", sections: ["province"] },
  { label: "Address", sections: ["billing", "shipping"] },
  { label: "Payment", sections: ["payment"] },
  { label: "Review", sections: [] },
];

const GRID = "grid grid-cols-1 gap-4 sm:grid-cols-2";
const WIDE = "sm:col-span-2";

const ADDRESS_FIELDS = [
  { name: "full_name", label: "Full name", autoComplete: "name", required: true, className: WIDE },
  { name: "address_line_1", label: "Address", autoComplete: "address-line1", required: true, className: WIDE },
  { name: "address_line_2", label: "Apartment, suite, etc. (optional)", autoComplete: "address-line2", className: WIDE },
  { name: "city", label: "City", autoComplete: "address-level2", required: true },
  { name: "postal_code", label: "Postal code", autoComplete: "postal-code", placeholder: "A1A 1A1", required: true },
];

const PAYMENT_FIELDS = [
  { name: "cardholder_name", label: "Name on card", autoComplete: "cc-name", required: true, className: WIDE },
  { name: "card_number", label: "Card number", inputMode: "numeric", autoComplete: "cc-number", placeholder: "4242 4242 4242 4242", required: true, className: WIDE },
  { name: "expiry_month", label: "Expiry month", type: "number", min: 1, max: 12, placeholder: "MM", required: true },
  { name: "expiry_year", label: "Expiry year", type: "number", min: 2000, placeholder: "YYYY", required: true },
  { name: "cvv", label: "CVV", type: "password", inputMode: "numeric", autoComplete: "cc-csc", maxLength: 4, required: true },
];

export default function Checkout() {
  const [step, setStep] = useState(0);
  const [checkout, setCheckout] = useState({ province: "", billing: {}, same_as_billing: true, shipping: {}, payment: {} });
  const [errors, setErrors] = useState({});
  const set = (changes) => setCheckout((current) => ({ ...current, ...changes }));

  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: cart, isPending } = useCart(checkout.province || null);
  const provinces = useQuery({ queryKey: ["provinces"], queryFn: getProvinces, staleTime: Infinity });
  const provinceName = provinces.data?.find((province) => province.code === checkout.province)?.name;

  const validate = useMutation({
    mutationFn: () => validateCheckout(checkout, STEPS[step].sections),
    onSuccess: () => { setErrors({}); setStep(step + 1); },
    onError: (error) => setErrors(errorsOf(error)),
  });
  const order = useMutation({
    mutationFn: () => placeOrder(checkout),
    onSuccess: (placed) => {
      queryClient.invalidateQueries({ queryKey: ["cart"] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      navigate(`/orders/${placed.id}`, { replace: true, state: { justPlaced: true } });
    },
    onError: (error) => {
      // Send the shopper back to the first step whose details failed (e.g. the card expired meanwhile).
      const failed = errorsOf(error);
      setErrors(failed);
      const failedStep = STEPS.findIndex(({ sections }) => sections.some((section) => failed[section]));
      if (failedStep >= 0) setStep(failedStep);
    },
  });

  if (isPending) return <Loading />;
  // Don't bounce away while the just-placed order is navigating to its confirmation page.
  if (!order.isSuccess && (cart.items.length === 0 || cart.has_errors)) return <Navigate to="/cart" replace />;

  const goTo = (index) => { setErrors({}); setStep(index); };
  const submit = (event) => {
    event.preventDefault();
    (step === STEPS.length - 1 ? order : validate).mutate();
  };
  const busy = validate.isPending || order.isPending;

  return (
    <div className="container mx-auto max-w-6xl px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold">Checkout</h1>
      <StepIndicator step={step} onSelect={goTo} />

      <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-3">
        <form onSubmit={submit} className="space-y-6 lg:col-span-2" noValidate>
          {errors.cart && (
            <Alert>{errors.cart.join(" ")} <Link to="/cart" className="font-semibold underline">Review your cart</Link></Alert>
          )}

          {step === 0 && (
            <section className="card">
              <h2 className="mb-1 text-xl font-semibold">Where are we shipping?</h2>
              <p className="mb-4 text-sm text-gray-600">Sales tax and shipping depend on the destination province.</p>
              <label htmlFor="province" className="mb-1 block text-sm font-medium text-gray-700">Province</label>
              <select id="province" className="input" value={checkout.province} onChange={(event) => set({ province: event.target.value })}>
                <option value="" disabled>Select a province</option>
                {provinces.data?.map((province) => (
                  <option key={province.code} value={province.code}>
                    {province.name} &mdash; {Number(province.shipping_cost) ? `${formatMoney(province.shipping_cost)} shipping` : "free shipping"}
                  </option>
                ))}
              </select>
              <FieldErrors errors={errors.province?.province} />
            </section>
          )}

          {step === 1 && (
            <>
              <section className="card">
                <h2 className="mb-4 text-xl font-semibold">Billing address</h2>
                <FieldGroup fields={ADDRESS_FIELDS} values={checkout.billing} errors={errors.billing} onChange={(billing) => set({ billing })} className={GRID} />
              </section>
              <section className="card space-y-4">
                <h2 className="text-xl font-semibold">Shipping address</h2>
                <Field type="checkbox" label="Ship to my billing address" checked={checkout.same_as_billing}
                  onChange={(event) => set({ same_as_billing: event.target.checked })} />
                {!checkout.same_as_billing && (
                  <FieldGroup fields={ADDRESS_FIELDS} values={checkout.shipping} errors={errors.shipping} onChange={(shipping) => set({ shipping })} className={GRID} />
                )}
              </section>
            </>
          )}

          {step === 2 && (
            <section className="card">
              <h2 className="mb-1 text-xl font-semibold">Payment</h2>
              <p className="mb-4 text-sm text-gray-600">This is a demo store: no card is charged and only the last four digits are kept.</p>
              <FieldGroup fields={PAYMENT_FIELDS} values={checkout.payment} errors={errors.payment} onChange={(payment) => set({ payment })} className={GRID} />
            </section>
          )}

          {step === 3 && (
            <Review checkout={checkout} provinceName={provinceName} onEdit={goTo} />
          )}

          <div className="flex items-center justify-between">
            {step > 0 ? (
              <button type="button" className="link font-medium" onClick={() => goTo(step - 1)}>&larr; Back</button>
            ) : (
              <Link to="/cart" className="link font-medium">&larr; Back to cart</Link>
            )}
            <button type="submit" className="btn-primary" disabled={busy || (step === 0 && !checkout.province)}>
              {step < STEPS.length - 1 ? `Continue to ${STEPS[step + 1].label.toLowerCase()}` : `Place order · ${formatMoney(cart.total)}`}
            </button>
          </div>
        </form>

        <aside className="card lg:sticky lg:top-4">
          <div className="mb-2 flex items-baseline justify-between">
            <h2 className="text-lg font-semibold">Order summary</h2>
            <Link to="/cart" className="link text-sm">Edit cart</Link>
          </div>
          <LineItems items={cart.items} />
          <div className="border-t border-gray-200 pt-4">
            <Totals totals={cart} showTax={Boolean(cart.province)} />
          </div>
        </aside>
      </div>
    </div>
  );
}

function StepIndicator({ step, onSelect }) {
  return (
    <ol className="mb-8 flex flex-wrap gap-2 text-sm">
      {STEPS.map(({ label }, index) => {
        const circle = "flex h-7 w-7 items-center justify-center rounded-full";
        return (
          <li key={label} className="flex items-center gap-2">
            {index < step ? (
              <button type="button" onClick={() => onSelect(index)} className="flex items-center gap-2 text-red-600 hover:underline">
                <span className={`${circle} bg-red-600 text-white`}>✓</span>{label}
              </button>
            ) : (
              <span aria-current={index === step ? "step" : undefined} className={`flex items-center gap-2 ${index === step ? "font-semibold" : "text-gray-400"}`}>
                <span className={`${circle} ${index === step ? "bg-red-600 text-white" : "border border-gray-300"}`}>{index + 1}</span>{label}
              </span>
            )}
            {index < STEPS.length - 1 && <span className="px-1 text-gray-300">&rsaquo;</span>}
          </li>
        );
      })}
    </ol>
  );
}

function Review({ checkout, provinceName, onEdit }) {
  const { payment } = checkout;
  const sections = [
    { title: "Billing", step: 1, body: <Address address={checkout.billing} /> },
    { title: "Shipping", step: 1, body: <Address address={checkout.same_as_billing ? checkout.billing : checkout.shipping} province={provinceName} /> },
    {
      title: "Payment",
      step: 2,
      body: (
        <p className="text-gray-700">
          {payment.cardholder_name}<br />
          Card ending in {String(payment.card_number).replace(/\D/g, "").slice(-4)}, expires {String(payment.expiry_month).padStart(2, "0")}/{payment.expiry_year}
        </p>
      ),
    },
  ];
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      {sections.map(({ title, step, body }) => (
        <section key={title} className="card">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">{title}</h2>
            <button type="button" className="link font-medium" onClick={() => onEdit(step)}>Edit</button>
          </div>
          {body}
        </section>
      ))}
    </div>
  );
}

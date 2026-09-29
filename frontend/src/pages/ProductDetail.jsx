import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { addToCart, errorsOf, getProduct } from "../api";
import { FieldErrors } from "../components/Field";
import { ProductGrid } from "../components/ProductCard";
import ProductImage from "../components/ProductImage";
import { Alert, Loading, PageError } from "../components/Status";
import StockBadge from "../components/StockBadge";
import { useCartMutation } from "../hooks/useCart";
import { formatMoney } from "../utils";

export default function ProductDetail() {
  const { slug } = useParams();
  const { data: product, isPending, error } = useQuery({ queryKey: ["product", slug], queryFn: () => getProduct(slug) });

  if (isPending) return <Loading />;
  if (error) return <PageError error={error} what="product" />;

  return (
    <div className="container mx-auto px-4 py-8">
      <nav aria-label="Breadcrumb" className="mb-6 text-sm">
        <Link to="/" className="link">Home</Link>
        <span className="text-gray-400"> / </span>
        <Link to="/products" className="link">Products</Link>
        {product.category && (
          <>
            <span className="text-gray-400"> / </span>
            <Link to={`/products?category=${product.category.slug}`} className="link">{product.category.name}</Link>
          </>
        )}
        <span className="text-gray-400"> / </span>
        <span className="text-gray-700">{product.name}</span>
      </nav>

      <div className="mb-12 grid grid-cols-1 gap-8 md:grid-cols-2">
        <div className="h-72 w-full rounded-lg bg-white p-4 shadow-md sm:h-96">
          <ProductImage product={product} />
        </div>

        <div>
          <h1 className="mb-4 text-4xl font-bold">{product.name}</h1>
          <p className="mb-6 text-4xl font-bold text-red-600">{formatMoney(product.price)}</p>
          <div className="mb-6"><StockBadge product={product} detailed /></div>
          <h2 className="mb-3 text-xl font-semibold">Description</h2>
          <p className="mb-8 leading-relaxed text-gray-700">{product.description}</p>

          {/* Keyed so options and quantity reset when navigating to a related product. */}
          {product.in_stock && <AddToCartForm key={product.slug} product={product} />}

          <dl className="grid grid-cols-2 gap-4 border-t border-gray-200 pt-6">
            <div><dt className="text-sm text-gray-600">SKU</dt><dd className="font-semibold">PROD-{product.id}</dd></div>
            <div><dt className="text-sm text-gray-600">Category</dt><dd className="font-semibold">{product.category?.name ?? "Uncategorized"}</dd></div>
          </dl>
        </div>
      </div>

      {product.related.length > 0 && (
        <section>
          <h2 className="mb-6 text-2xl font-bold">You may also like</h2>
          <ProductGrid products={product.related} className="sm:grid-cols-2 lg:grid-cols-4" />
        </section>
      )}
    </div>
  );
}

function AddToCartForm({ product }) {
  const [quantity, setQuantity] = useState(1);
  const [variations, setVariations] = useState(() =>
    Object.fromEntries(product.variation_groups.map((group) => [group.category, group.options[0]?.id])),
  );
  const add = useCartMutation(addToCart);
  const errors = add.isError ? errorsOf(add.error) : {};

  const submit = (event) => {
    event.preventDefault();
    add.mutate({ product: product.slug, quantity, variations });
  };

  return (
    <form onSubmit={submit} className="mb-8 space-y-4">
      {add.isSuccess && (
        <Alert tone="success">
          Added {product.name} to your cart. <Link to="/cart" className="font-semibold underline">View cart</Link>
        </Alert>
      )}
      <FieldErrors errors={errors.__all__} />

      {product.variation_groups.map((group) => (
        <div key={group.category}>
          <label htmlFor={`variation-${group.category}`} className="mb-1 block text-sm font-medium text-gray-700">{group.label}</label>
          <select
            id={`variation-${group.category}`}
            className="input"
            value={variations[group.category]}
            onChange={(event) => setVariations({ ...variations, [group.category]: Number(event.target.value) })}
          >
            {group.options.map((option) => <option key={option.id} value={option.id}>{option.value}</option>)}
          </select>
          <FieldErrors errors={errors[`variation_${group.category}`]} />
        </div>
      ))}

      <div>
        <label htmlFor="quantity" className="mb-1 block text-sm font-medium text-gray-700">Quantity</label>
        <div className="flex gap-2">
          <input
            id="quantity"
            type="number"
            min="1"
            max={product.stock}
            value={quantity}
            onChange={(event) => setQuantity(event.target.value === "" ? "" : Number(event.target.value))}
            className="input w-20 text-center"
            required
          />
          <button type="submit" className="btn-primary flex-1" disabled={add.isPending}>
            {add.isPending ? "Adding..." : "Add to Cart"}
          </button>
        </div>
        <FieldErrors errors={errors.quantity} />
      </div>
    </form>
  );
}

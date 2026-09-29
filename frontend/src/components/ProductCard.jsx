import { Link } from "react-router-dom";

import { formatMoney } from "../utils";
import ProductImage from "./ProductImage";
import StockBadge from "./StockBadge";

export default function ProductCard({ product }) {
  const url = `/products/${product.slug}`;
  return (
    <article className="group flex h-full flex-col overflow-hidden rounded-lg bg-white shadow-md transition hover:shadow-lg">
      <Link to={url} tabIndex={-1} className="block h-48 p-2">
        <ProductImage product={product} />
      </Link>
      <div className="flex flex-1 flex-col p-4">
        {product.category && <p className="text-xs uppercase tracking-wide text-gray-500">{product.category.name}</p>}
        <h3 className="mt-1">
          <Link to={url} className="text-lg font-semibold text-gray-800 group-hover:text-red-600">{product.name}</Link>
        </h3>
        <p className="mt-2 line-clamp-2 text-sm text-gray-600">{product.description}</p>
        <div className="mt-auto flex items-center justify-between pt-4">
          <span className="text-xl font-bold text-red-600">{formatMoney(product.price)}</span>
          <StockBadge product={product} />
        </div>
      </div>
    </article>
  );
}

export function ProductGrid({ products, className = "sm:grid-cols-2 lg:grid-cols-3" }) {
  return (
    <div className={`grid grid-cols-1 gap-6 ${className}`}>
      {products.map((product) => <ProductCard key={product.id} product={product} />)}
    </div>
  );
}

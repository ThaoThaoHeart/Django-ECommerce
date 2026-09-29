export default function StockBadge({ product, detailed = false }) {
  if (!product.in_stock) {
    return <span className="rounded bg-red-100 px-2 py-1 text-xs font-semibold text-red-700">Out of Stock</span>;
  }
  return (
    <span className="rounded bg-green-100 px-2 py-1 text-xs font-semibold text-green-700">
      In Stock{detailed && ` (${product.stock} available)`}
    </span>
  );
}

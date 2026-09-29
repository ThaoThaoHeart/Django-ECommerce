export default function ProductImage({ product, className = "" }) {
  if (product.image) {
    return <img src={product.image} alt={product.name} className={`h-full w-full object-contain ${className}`} />;
  }
  return (
    <div role="img" aria-label={product.name} className={`flex h-full w-full items-center justify-center rounded-lg bg-gradient-to-br from-gray-200 to-gray-300 ${className}`}>
      <span className="text-4xl font-bold text-gray-500">{product.name.charAt(0)}</span>
    </div>
  );
}

import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getCategories, getProducts } from "../api";
import { ProductGrid } from "../components/ProductCard";
import { Loading } from "../components/Status";
import { pluralize } from "../utils";

export default function Home() {
  const categories = useQuery({ queryKey: ["categories"], queryFn: getCategories });
  const newest = useQuery({ queryKey: ["products", { sort: "-created_at", page_size: 8 }], queryFn: ({ queryKey }) => getProducts(queryKey[1]) });

  return (
    <>
      <section className="bg-gradient-to-r from-gray-900 to-red-900 text-white">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <h1 className="max-w-2xl text-4xl font-bold md:text-5xl">Instruments and gear for every musician</h1>
          <p className="mt-4 max-w-xl text-lg text-gray-200">Guitars, keyboards, drums and studio software, shipped anywhere in Canada.</p>
          <Link to="/products" className="btn-primary mt-8">Shop all products</Link>
        </div>
      </section>

      <div className="container mx-auto space-y-12 px-4 py-12">
        <section>
          <h2 className="mb-6 text-2xl font-bold">Shop by category</h2>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {categories.data?.filter((category) => category.product_count > 0).map((category) => (
              <Link
                key={category.id}
                to={`/products?category=${category.slug}`}
                className="rounded-lg bg-white p-6 shadow-md transition hover:shadow-lg hover:ring-2 hover:ring-red-500"
              >
                <p className="text-lg font-semibold">{category.name}</p>
                <p className="text-sm text-gray-500">{pluralize(category.product_count, "product")}</p>
              </Link>
            ))}
          </div>
        </section>

        <section>
          <div className="mb-6 flex items-baseline justify-between">
            <h2 className="text-2xl font-bold">New arrivals</h2>
            <Link to="/products?sort=-created_at" className="link">View all</Link>
          </div>
          {newest.isPending ? <Loading /> : <ProductGrid products={newest.data?.results ?? []} className="sm:grid-cols-2 lg:grid-cols-4" />}
        </section>
      </div>
    </>
  );
}

import { useState } from "react";
import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";

import { getCategories, getProducts } from "../api";
import Pagination from "../components/Pagination";
import { ProductGrid } from "../components/ProductCard";
import { Loading, PageError } from "../components/Status";
import { pluralize } from "../utils";

const SORT_OPTIONS = [
  ["name", "Name: A to Z"],
  ["-name", "Name: Z to A"],
  ["price", "Price: low to high"],
  ["-price", "Price: high to low"],
  ["-created_at", "Newest"],
];
const FILTER_KEYS = ["q", "category", "min_price", "max_price", "in_stock"];

export default function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const params = Object.fromEntries(searchParams);
  const [showFilters, setShowFilters] = useState(false);

  const categories = useQuery({ queryKey: ["categories"], queryFn: getCategories });
  const products = useQuery({
    queryKey: ["products", params],
    queryFn: () => getProducts(params),
    placeholderData: keepPreviousData,
  });

  /** Merge changes into the URL; empty values are dropped and any filter change resets to page 1. */
  const update = (changes) => {
    const next = { ...params, page: undefined, ...changes };
    setSearchParams(Object.fromEntries(Object.entries(next).filter(([, value]) => value !== undefined && value !== "")));
  };

  const selectedCategory = categories.data?.find((category) => category.slug === params.category);
  const hasFilters = FILTER_KEYS.some((key) => params[key]);
  const clearFilters = () => setSearchParams(params.sort ? { sort: params.sort } : {});

  if (products.isError) return <PageError error={products.error} what="page" />;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">{selectedCategory?.name ?? "All Products"}</h1>
          <p className="mt-1 text-gray-600"><ResultCount data={products.data} query={params.q} /></p>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" className="btn-secondary px-4 py-2 md:hidden" onClick={() => setShowFilters((shown) => !shown)}>
            {showFilters ? "Hide filters" : "Filters"}
          </button>
          <label htmlFor="sort" className="text-sm text-gray-700">Sort by</label>
          <select id="sort" className="input w-auto" value={params.sort ?? "name"} onChange={(event) => update({ sort: event.target.value })}>
            {SORT_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-8 md:grid-cols-4">
        <aside className={`space-y-6 md:block ${showFilters ? "" : "hidden"}`}>
          <section className="card p-4 md:p-4">
            <h2 className="mb-3 text-lg font-semibold">Categories</h2>
            <ul className="space-y-1">
              <CategoryLink active={!params.category} onClick={() => update({ category: undefined })} label="All Categories" />
              {categories.data?.map((category) => (
                <CategoryLink
                  key={category.id}
                  active={params.category === category.slug}
                  onClick={() => update({ category: category.slug })}
                  label={category.name}
                  count={category.product_count}
                />
              ))}
            </ul>
          </section>
          {/* Keyed on the URL so the inputs reset when filters change elsewhere (navbar search, Clear). */}
          <FilterForm key={searchParams.toString()} params={params} onApply={update} onClear={hasFilters ? clearFilters : null} />
        </aside>

        <div className={`md:col-span-3 transition-opacity ${products.isPlaceholderData ? "opacity-60" : ""}`}>
          {products.isPending ? (
            <Loading />
          ) : products.data.results.length ? (
            <>
              <ProductGrid products={products.data.results} />
              <Pagination page={products.data.page} numPages={products.data.num_pages} onChange={(page) => update({ page })} />
            </>
          ) : (
            <div className="card py-12 text-center">
              <p className="text-lg text-gray-500">No products match your filters.</p>
              {hasFilters && <button type="button" className="link mt-3" onClick={clearFilters}>Clear all filters</button>}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ResultCount({ data, query }) {
  if (!data) return null;
  if (!data.count) return "No products found";
  return (
    <>
      Showing {data.start_index}&ndash;{data.end_index} of {pluralize(data.count, "product")}
      {query && <> for &ldquo;{query}&rdquo;</>}
    </>
  );
}

function CategoryLink({ active, onClick, label, count }) {
  return (
    <li>
      <button
        type="button"
        onClick={onClick}
        aria-current={active || undefined}
        className={`flex w-full justify-between rounded px-3 py-2 text-left ${active ? "bg-red-100 font-semibold text-red-700" : "text-gray-700 hover:bg-gray-100"}`}
      >
        <span>{label}</span>
        {count !== undefined && <span className="text-gray-400">{count}</span>}
      </button>
    </li>
  );
}

function FilterForm({ params, onApply, onClear }) {
  const [values, setValues] = useState({
    q: params.q ?? "",
    min_price: params.min_price ?? "",
    max_price: params.max_price ?? "",
    in_stock: params.in_stock === "true",
  });
  const set = (name) => (event) =>
    setValues({ ...values, [name]: event.target.type === "checkbox" ? event.target.checked : event.target.value });

  const submit = (event) => {
    event.preventDefault();
    onApply({ ...values, in_stock: values.in_stock ? "true" : undefined });
  };

  return (
    <form onSubmit={submit} className="card space-y-4 p-4 md:p-4">
      <h2 className="text-lg font-semibold">Filters</h2>
      <div>
        <label htmlFor="filter-q" className="mb-1 block text-sm font-medium text-gray-700">Search</label>
        <input id="filter-q" type="search" className="input" value={values.q} onChange={set("q")} placeholder="Search products..." />
      </div>
      <fieldset>
        <legend className="mb-1 block text-sm font-medium text-gray-700">Price</legend>
        <div className="flex items-center gap-2">
          <input type="number" min="0" step="any" className="input" aria-label="Minimum price" placeholder="Min" value={values.min_price} onChange={set("min_price")} />
          <span className="text-gray-400">&ndash;</span>
          <input type="number" min="0" step="any" className="input" aria-label="Maximum price" placeholder="Max" value={values.max_price} onChange={set("max_price")} />
        </div>
      </fieldset>
      <label className="inline-flex items-center gap-2 text-sm font-medium text-gray-700">
        <input type="checkbox" className="h-4 w-4 accent-red-600" checked={values.in_stock} onChange={set("in_stock")} />
        In stock only
      </label>
      <button type="submit" className="btn-primary w-full py-2">Apply filters</button>
      {onClear && <button type="button" onClick={onClear} className="link block w-full text-center text-sm">Clear all filters</button>}
    </form>
  );
}

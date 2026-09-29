import { Link } from "react-router-dom";

export function Loading() {
  return (
    <div className="flex justify-center py-16" role="status" aria-label="Loading">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-300 border-t-red-600" />
    </div>
  );
}

export function Alert({ tone = "error", children }) {
  const tones = {
    error: "bg-red-100 text-red-800",
    success: "bg-green-100 text-green-800",
    info: "bg-blue-100 text-blue-800",
  };
  return <div role="alert" className={`rounded-lg px-4 py-3 text-sm ${tones[tone]}`}>{children}</div>;
}

/** Full-page message for a failed query: a 404 reads as "not found", anything else as a load error. */
export function PageError({ error, what = "page" }) {
  const notFound = error?.response?.status === 404;
  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <h1 className="text-3xl font-bold">{notFound ? `We couldn't find that ${what}` : "Something went wrong"}</h1>
      <p className="mt-2 text-gray-600">{notFound ? "It may have been moved or removed." : "Please refresh the page to try again."}</p>
      <Link to="/products" className="btn-primary mt-6">Browse products</Link>
    </div>
  );
}

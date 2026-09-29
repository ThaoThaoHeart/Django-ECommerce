const ELLIPSIS = "…";

/** Page numbers with the ends and the current page's neighbours, eliding the rest (like Django's). */
function pageRange(page, numPages, around = 1) {
  const pages = [];
  for (let n = 1; n <= numPages; n += 1) {
    if (n === 1 || n === numPages || Math.abs(n - page) <= around) pages.push(n);
    else if (pages.at(-1) !== ELLIPSIS) pages.push(ELLIPSIS);
  }
  return pages;
}

export default function Pagination({ page, numPages, onChange }) {
  if (numPages <= 1) return null;
  const button = "rounded-lg border border-gray-300 bg-white px-3 py-2 hover:bg-gray-50";

  return (
    <nav aria-label="Pagination" className="mt-8 flex flex-wrap items-center justify-center gap-1">
      {page > 1 && <button type="button" className={button} onClick={() => onChange(page - 1)}>&larr; Prev</button>}
      {pageRange(page, numPages).map((n, index) =>
        n === ELLIPSIS ? (
          <span key={`gap-${index}`} className="px-2 py-2 text-gray-500">{n}</span>
        ) : n === page ? (
          <span key={n} aria-current="page" className="rounded-lg bg-red-600 px-3 py-2 font-semibold text-white">{n}</span>
        ) : (
          <button key={n} type="button" className={button} onClick={() => onChange(n)}>{n}</button>
        ),
      )}
      {page < numPages && <button type="button" className={button} onClick={() => onChange(page + 1)}>Next &rarr;</button>}
    </nav>
  );
}

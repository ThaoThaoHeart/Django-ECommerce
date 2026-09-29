import axios from "axios";

// Django reads the CSRF token from this header; axios copies it from the cookie on same-origin requests.
const api = axios.create({
  baseURL: "/api",
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

const data = (request) => request.then((response) => response.data);

// Auth
export const getMe = () => data(api.get("/auth/me/")).then((body) => body.user);
export const login = (credentials) => data(api.post("/auth/login/", credentials)).then((body) => body.user);
export const register = (details) => data(api.post("/auth/register/", details)).then((body) => body.user);
export const logout = () => data(api.post("/auth/logout/")).then((body) => body.user);

// Catalog
export const getCategories = () => data(api.get("/categories/"));
export const getProducts = (params) => data(api.get("/products/", { params }));
export const getProduct = (slug) => data(api.get(`/products/${slug}/`));

// Cart: every mutation responds with the updated cart summary.
export const getCart = (province) => data(api.get("/cart/", { params: province ? { province } : {} }));
export const addToCart = (line) => data(api.post("/cart/items/", line));
export const updateCartItem = (id, quantity) => data(api.patch(`/cart/items/${id}/`, { quantity }));
export const removeCartItem = (id) => data(api.delete(`/cart/items/${id}/`));

// Checkout & orders
export const getProvinces = () => data(api.get("/provinces/"));
export const validateCheckout = (payload, sections) => data(api.post("/checkout/validate/", { ...payload, sections }));
export const placeOrder = (payload) => data(api.post("/checkout/", payload));
export const getOrders = () => data(api.get("/orders/"));
export const getOrder = (id) => data(api.get(`/orders/${id}/`));

/** Field errors from a failed request, shaped {field: [messages]}; "__all__" holds the rest. */
export function errorsOf(error) {
  return error?.response?.data?.errors ?? { __all__: ["Something went wrong. Please try again."] };
}

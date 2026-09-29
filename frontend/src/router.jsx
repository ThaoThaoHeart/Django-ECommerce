import { createBrowserRouter } from "react-router-dom";

import Layout from "./components/Layout";
import RequireAuth from "./components/RequireAuth";
import Account from "./pages/Account";
import AuthPage from "./pages/AuthPage";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import Home from "./pages/Home";
import NotFound from "./pages/NotFound";
import OrderDetail from "./pages/OrderDetail";
import ProductDetail from "./pages/ProductDetail";
import ProductList from "./pages/ProductList";

export const routes = [
  {
    element: <Layout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/products", element: <ProductList /> },
      { path: "/products/:slug", element: <ProductDetail /> },
      { path: "/cart", element: <Cart /> },
      { path: "/login", element: <AuthPage mode="login" /> },
      { path: "/register", element: <AuthPage mode="register" /> },
      {
        element: <RequireAuth />,
        children: [
          { path: "/checkout", element: <Checkout /> },
          { path: "/account", element: <Account /> },
          { path: "/orders/:id", element: <OrderDetail /> },
        ],
      },
      { path: "*", element: <NotFound /> },
    ],
  },
];

export const router = createBrowserRouter(routes);

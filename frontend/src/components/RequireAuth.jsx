import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { Loading } from "./Status";

export default function RequireAuth() {
  const { user, isPending } = useAuth();
  const location = useLocation();

  if (isPending) return <Loading />;
  if (!user) return <Navigate to={`/login?${new URLSearchParams({ next: location.pathname + location.search })}`} replace />;
  return <Outlet />;
}

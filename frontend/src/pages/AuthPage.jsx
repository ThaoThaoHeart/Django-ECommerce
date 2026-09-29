import { useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";

import { errorsOf } from "../api";
import { FieldGroup } from "../components/Field";
import { useAuth } from "../hooks/useAuth";

const MODES = {
  login: {
    title: "Login",
    submit: "Login",
    fields: [
      { name: "email", label: "Email", type: "email", autoComplete: "email", required: true, autoFocus: true },
      { name: "password", label: "Password", type: "password", autoComplete: "current-password", required: true },
    ],
    switchPrompt: "Don't have an account?",
    switchLabel: "Create one",
    switchTo: "/register",
  },
  register: {
    title: "Create Account",
    submit: "Register",
    fields: [
      { name: "email", label: "Email", type: "email", autoComplete: "email", required: true, autoFocus: true },
      { name: "password1", label: "Password", type: "password", autoComplete: "new-password", required: true },
      { name: "password2", label: "Confirm password", type: "password", autoComplete: "new-password", required: true },
    ],
    switchPrompt: "Already have an account?",
    switchLabel: "Login",
    switchTo: "/login",
  },
};

/** Only follow same-site paths from ?next= so the link can't bounce users to another site. */
const safeNext = (next) => (next?.startsWith("/") && !next.startsWith("//") ? next : "/");

export default function AuthPage({ mode }) {
  const config = MODES[mode];
  const [searchParams] = useSearchParams();
  const next = safeNext(searchParams.get("next"));
  const navigate = useNavigate();
  const auth = useAuth();
  const mutation = auth[mode];
  const [values, setValues] = useState({});

  if (auth.user && !mutation.isSuccess) return <Navigate to={next} replace />;

  const submit = (event) => {
    event.preventDefault();
    mutation.mutate(values, { onSuccess: () => navigate(next, { replace: true }) });
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="card mx-auto max-w-md">
        <h1 className="mb-6 text-3xl font-bold">{config.title}</h1>
        <form onSubmit={submit} className="space-y-6">
          <FieldGroup fields={config.fields} values={values} errors={mutation.isError ? errorsOf(mutation.error) : {}} onChange={setValues} />
          <button type="submit" className="btn-primary w-full py-2" disabled={mutation.isPending}>{config.submit}</button>
          <p className="text-center text-sm text-gray-600">
            {config.switchPrompt}{" "}
            <Link to={`${config.switchTo}?${new URLSearchParams({ next })}`} className="link font-semibold">{config.switchLabel}</Link>
          </p>
        </form>
      </div>
    </div>
  );
}

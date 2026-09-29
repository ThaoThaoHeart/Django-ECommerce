import { useId } from "react";

/** Labelled input with its validation errors. `errors` is the list of messages the API returned. */
export function Field({ label, errors, type = "text", ...inputProps }) {
  const id = useId();
  if (type === "checkbox") {
    return (
      <label className="inline-flex items-center gap-2 text-sm font-medium text-gray-700">
        <input type="checkbox" className="h-4 w-4 accent-red-600" {...inputProps} />
        {label}
      </label>
    );
  }
  return (
    <div>
      <label htmlFor={id} className="mb-1 block text-sm font-medium text-gray-700">{label}</label>
      <input id={id} type={type} className="input" aria-invalid={errors ? true : undefined} {...inputProps} />
      <FieldErrors errors={errors} />
    </div>
  );
}

export function FieldErrors({ errors }) {
  return errors?.map((message) => <p key={message} className="mt-1 text-sm text-red-600">{message}</p>) ?? null;
}

/**
 * Renders a list of field specs ({name, label, ...inputProps}) bound to one object of values.
 * Used for addresses, payment and the auth forms.
 */
export function FieldGroup({ fields, values, errors = {}, onChange, className = "space-y-4" }) {
  return (
    <div className={className}>
      <FieldErrors errors={errors.__all__} />
      {fields.map(({ name, className: fieldClass, ...props }) => (
        <div key={name} className={fieldClass}>
          <Field
            name={name}
            value={values[name] ?? ""}
            onChange={(event) => onChange({ ...values, [name]: event.target.value })}
            errors={errors[name]}
            {...props}
          />
        </div>
      ))}
    </div>
  );
}

export default function FormField({ label, ...props }) {
  return (
    <label className="field-block">
      <span>{label}</span>
      <input {...props} />
    </label>
  );
}

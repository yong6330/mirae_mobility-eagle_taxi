export default function StepCard({ step, title, text }) {
  return (
    <article className="step-card" tabIndex={0}>
      <span>{step}</span>
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

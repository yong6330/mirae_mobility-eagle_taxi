export default function FeatureCard({ icon: Icon, title, text }) {
  return (
    <article className="feature-card">
      <Icon size={24} />
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

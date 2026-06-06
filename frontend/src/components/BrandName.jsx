export default function BrandName({ className = '' }) {
  return (
    <span className={`brand-name ${className}`.trim()}>
      <span className="brand-name-eagle">Eagle</span>
      <span className="brand-name-taxi">Taxi</span>
    </span>
  );
}

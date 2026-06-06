export default function EagleMark({ small = false }) {
  return (
    <span className={`eagle-mark ${small ? 'small' : ''}`} aria-hidden="true">
      <img src="/assets/eagle-logo.png" alt="" />
    </span>
  );
}

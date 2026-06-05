export default function EagleMark({ small = false }) {
  return (
    <span className={`eagle-mark ${small ? 'small' : ''}`} aria-hidden="true">
      <span />
      <i />
      <span />
    </span>
  );
}

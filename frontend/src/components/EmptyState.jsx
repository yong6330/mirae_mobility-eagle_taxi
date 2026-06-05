import { ClipboardList } from 'lucide-react';

export default function EmptyState({ action, icon: Icon = ClipboardList, text, title }) {
  return (
    <div className="empty-state">
      <Icon size={30} />
      <strong>{title}</strong>
      <p>{text}</p>
      {action}
    </div>
  );
}

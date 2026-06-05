import { Loader2 } from 'lucide-react';
import EagleMark from './EagleMark';

export default function LoadingScreen() {
  return (
    <main className="loading-screen">
      <EagleMark />
      <Loader2 className="spin" size={28} />
      <h1>독수리 택시</h1>
      <p>서비스 상태를 확인하고 있습니다.</p>
    </main>
  );
}

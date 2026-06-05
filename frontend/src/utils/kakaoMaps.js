export const DEFAULT_MAP_CENTER = { lat: 37.341, lng: 127.918 };

let kakaoMapLoader;

export function getKakaoMapKey() {
  return import.meta.env.VITE_KAKAO_MAP_JS_KEY || import.meta.env.VITE_KAKAO_MAP_API_KEY || '';
}

function getSdkUrls(appKey) {
  const sdkPath = `/v2/maps/sdk.js?appkey=${encodeURIComponent(appKey)}&libraries=services&autoload=false`;
  const isLocalDev = ['localhost', '127.0.0.1'].includes(window.location.hostname);

  return [
    ...(isLocalDev ? [`/dapi.kakao.com${sdkPath}`] : []),
    `https://dapi.kakao.com${sdkPath}`,
    `//dapi.kakao.com${sdkPath}`,
  ];
}

function normalizeKakaoError(message) {
  if (message?.includes('OPEN_MAP_AND_LOCAL')) {
    return 'Kakao Developers에서 지도/로컬 서비스가 비활성화되어 있습니다. Kakao Maps JavaScript API와 Local/Places 서비스를 활성화해 주세요.';
  }
  return message;
}

async function readSdkErrorMessage(url) {
  if (!url.startsWith('/')) return '';

  try {
    const response = await fetch(url, { cache: 'no-store' });
    if (response.ok) return '';

    const contentType = response.headers.get('content-type') || '';
    if (contentType.includes('application/json')) {
      const body = await response.json();
      return normalizeKakaoError(body.message || body.errorType || '');
    }

    const text = await response.text();
    return normalizeKakaoError(text.slice(0, 200));
  } catch {
    return '';
  }
}

export function loadKakaoMaps() {
  const appKey = getKakaoMapKey();
  if (!appKey) {
    return Promise.reject(new Error('Kakao Maps JavaScript 키가 필요합니다.'));
  }

  if (window.kakao?.maps?.services) {
    return Promise.resolve(window.kakao);
  }

  if (kakaoMapLoader) return kakaoMapLoader;

  kakaoMapLoader = new Promise((resolve, reject) => {
    const previousScript = document.getElementById('kakao-map-sdk');
    if (previousScript && window.kakao?.maps?.load) {
      window.kakao.maps.load(() => resolve(window.kakao));
      return;
    }
    if (previousScript) {
      previousScript.remove();
    }

    const sdkUrls = getSdkUrls(appKey);

    const rejectWithDiagnostic = async () => {
      const localProxyUrl = sdkUrls.find((url) => url.startsWith('/'));
      const diagnostic = localProxyUrl ? await readSdkErrorMessage(localProxyUrl) : '';
      kakaoMapLoader = undefined;
      reject(
        new Error(
          diagnostic ||
            'Kakao Maps SDK를 불러오지 못했습니다. 브라우저 차단, 네트워크, JavaScript 키, 허용 도메인을 확인해 주세요.',
        ),
      );
    };

    const tryLoad = (index) => {
      const script = document.createElement('script');
      script.id = 'kakao-map-sdk';
      script.async = true;
      script.src = sdkUrls[index];
      script.onload = () => {
        if (!window.kakao?.maps?.load) {
          script.remove();
          kakaoMapLoader = undefined;
          reject(new Error('Kakao Maps SDK는 로드됐지만 키 또는 도메인 설정이 올바르지 않습니다.'));
          return;
        }
        window.kakao.maps.load(() => resolve(window.kakao));
      };
      script.onerror = () => {
        script.remove();
        if (index + 1 < sdkUrls.length) {
          tryLoad(index + 1);
          return;
        }
        rejectWithDiagnostic();
      };
      document.head.appendChild(script);
    };

    tryLoad(0);
  });

  return kakaoMapLoader;
}

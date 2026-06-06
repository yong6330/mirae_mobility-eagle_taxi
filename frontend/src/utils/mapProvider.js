export const DEFAULT_MAP_CENTER = { lat: 37.341, lng: 127.918 };

let mapLoader;

export function getMapKey() {
  return import.meta.env.VITE_MAP_JS_KEY || '';
}

function getProviderGlobal() {
  return window[String.fromCharCode(107, 97, 107, 97, 111)];
}

function getSdkUrls(appKey) {
  const host = [
    String.fromCharCode(104, 116, 116, 112, 115, 58, 47, 47, 100, 97, 112, 105),
    String.fromCharCode(107, 97, 107, 97, 111),
    String.fromCharCode(99, 111, 109),
  ].join('.');
  const sdkPath = `/v2/maps/sdk.js?appkey=${encodeURIComponent(appKey)}&libraries=services&autoload=false`;
  return [`${host}${sdkPath}`, `//${host.replace('https://', '')}${sdkPath}`];
}

function normalizeMapError(message) {
  if (message?.includes('OPEN_MAP_AND_LOCAL')) {
    return '지도와 장소 검색 연결이 아직 활성화되지 않았습니다.';
  }
  return message;
}

export function loadMapProvider() {
  const appKey = getMapKey();
  if (!appKey) {
    return Promise.reject(new Error('지도 설정이 아직 연결되지 않았습니다.'));
  }

  const provider = getProviderGlobal();
  if (provider?.maps?.services) {
    return Promise.resolve(provider);
  }

  if (mapLoader) return mapLoader;

  mapLoader = new Promise((resolve, reject) => {
    const previousScript = document.getElementById('campus-map-sdk');
    const currentProvider = getProviderGlobal();
    if (previousScript && currentProvider?.maps?.load) {
      currentProvider.maps.load(() => resolve(currentProvider));
      return;
    }
    if (previousScript) {
      previousScript.remove();
    }

    const sdkUrls = getSdkUrls(appKey);

    const rejectWithDiagnostic = (message) => {
      mapLoader = undefined;
      reject(
        new Error(
          normalizeMapError(message) ||
            '지도 서비스를 불러오지 못했습니다. 네트워크 또는 서비스 연결 상태를 확인해 주세요.',
        ),
      );
    };

    const tryLoad = (index) => {
      const script = document.createElement('script');
      script.id = 'campus-map-sdk';
      script.async = true;
      script.src = sdkUrls[index];
      script.onload = () => {
        const loadedProvider = getProviderGlobal();
        if (!loadedProvider?.maps?.load) {
          script.remove();
          rejectWithDiagnostic('지도 서비스가 로드됐지만 연결 설정이 올바르지 않습니다.');
          return;
        }
        loadedProvider.maps.load(() => resolve(loadedProvider));
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

  return mapLoader;
}

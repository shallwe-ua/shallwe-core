'use client';

import { ReactNode, useEffect, useState } from 'react';

export function InitMSW({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(process.env.NEXT_PUBLIC_SHALLWE_MOCK_API !== 'true');

  useEffect(() => {
    if (process.env.NEXT_PUBLIC_SHALLWE_MOCK_API === 'true') {
      import('../mocks/browser').then(({ worker }) => {
        worker.start({onUnhandledRequest: 'bypass', }).then(() => {
            setReady(true);
          });
      });
    }
  }, []);

  return !ready ? null : <>{children}</>;
}

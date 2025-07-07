import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('*/api/rest/auth/login/google/', () =>
    HttpResponse.json({ key: 'mock-key' }, { status: 200 })
  ),

  http.get('*/api/rest/auth/test-api-unprotected/', () =>
    HttpResponse.json({ message: 'Hello! Make yourself at home!' })
  ),

  http.get('*/api/rest/access/profile-status', () =>
    new HttpResponse(null, { status: 200 })
  ),
];

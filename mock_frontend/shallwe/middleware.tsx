import { NextRequest, NextResponse } from 'next/server';

const apiBaseUrl = process.env.NEXT_PUBLIC_SHALLWE_API_BASE_URL || '';

export async function middleware(request: NextRequest) {

    const url = request.nextUrl.clone();

    // Check if the URL starts with /admin
    if (url.pathname.startsWith('/admin')) {
    // Update hostname and port based on the environment variable
    const apiUrl = new URL(apiBaseUrl);

    url.hostname = apiUrl.hostname;
    url.port = apiUrl.port;
    url.protocol = apiUrl.protocol;
    url.pathname = '/admin' + url.pathname.slice('/admin'.length);

    // Remove the ?next=... query parameter if present
    url.searchParams.delete('next');

    // Redirect to the new URL
    return NextResponse.redirect(url);
    }

  const res = await fetch(`${apiBaseUrl}/api/rest/access/profile-status`, {
    headers: {
      'Cookie': request.headers.get('cookie') || ''
    }
  });

  if (res.status === 403 && request.nextUrl.pathname !== '/') {
    return NextResponse.redirect(new URL('/', request.url));
  }

  if (res.status === 404 && request.nextUrl.pathname !== '/setup') {
    return NextResponse.redirect(new URL('/setup', request.url));
  }

  if (res.status === 200) {
    if (request.nextUrl.pathname === '/') {
      return NextResponse.redirect(new URL('/search', request.url));
    }
    if (request.nextUrl.pathname === '/setup') {
      return NextResponse.redirect(new URL('/settings', request.url));
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/', '/setup', '/settings', '/contacts', '/search', '/admin/:path*'],
};

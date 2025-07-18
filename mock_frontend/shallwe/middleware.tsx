import { NextRequest, NextResponse } from 'next/server';
import { env } from "@/config/env";


const apiBaseUrl = env.NEXT_PUBLIC_SHALLWE_API_BASE_URL || '';
const skipMiddleware = env.NEXT_PUBLIC_SHALLWE_SKIP_MIDDLEWARE === 'true';


export async function middleware(request: NextRequest) {

    // If in mock mode, skip all auth/profile checks
    if (skipMiddleware) {
        return NextResponse.next();
    }

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

    const cookie = request.headers.get('cookie')

    const url2 = `${apiBaseUrl}/api/rest/access/profile-status`;

    // Create headers object
    const headers = new Headers({
        'Content-Type': 'application/json'
    });

    // Only set the cookie header if it's not null
    if (cookie) {
        headers.append('Cookie', cookie);
    }

    // Create a new request object with headers
    const req = new Request(url2, {
        method: 'GET', // Use the appropriate method
        headers: headers,
        credentials: 'include' // Include credentials to send cookies
    });

    // Log the headers before sending the request
    req.headers.forEach((value, key) => {
        console.log(`${key}: ${value}`);
    });

    // Send the request
    const res = await fetch(req);

    // If you also want to log the response headers
    res.headers.forEach((value, key) => {
        console.log(`Response Header - ${key}: ${value}`);
    });

    console.log(`Profile status check: ${res.status}`)

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

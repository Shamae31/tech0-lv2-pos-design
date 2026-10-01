import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const base = process.env.API_BASE_URL || (process.env.NODE_ENV === 'development' ? 'http://127.0.0.1:8000' : '');
  if (!base || (process.env.NODE_ENV === 'production' && !base.startsWith('https://'))) {
    return NextResponse.json({ detail: 'API接続設定がありません' }, { status: 503 });
  }

  const { path } = await context.params;
  const target = `${base.replace(/\/$/, '')}/api/${path.map(encodeURIComponent).join('/')}${request.nextUrl.search}`;
  try {
    const upstream = await fetch(target, {
      method: request.method,
      headers: {
        ...(request.headers.get('authorization') ? { authorization: request.headers.get('authorization')! } : {}),
        ...(request.headers.get('content-type') ? { 'content-type': request.headers.get('content-type')! } : {}),
      },
      body: request.method === 'POST' ? await request.text() : undefined,
      cache: 'no-store',
    });
    return new NextResponse(await upstream.text(), {
      status: upstream.status,
      headers: { 'content-type': upstream.headers.get('content-type') || 'application/json', 'cache-control': 'no-store' },
    });
  } catch {
    return NextResponse.json({ detail: 'APIに接続できません' }, { status: 502 });
  }
}

export { proxy as GET, proxy as POST };

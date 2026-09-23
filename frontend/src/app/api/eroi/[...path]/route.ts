import {
  NextRequest,
  NextResponse,
} from "next/server";


const BACKEND_URL =
  process.env.EROI_BACKEND_URL ||
  "http://127.0.0.1:8000";


async function proxyRequest(
  request: NextRequest,
  path: string[]
) {

  const backendPath =
    "/" + path.join("/");

  const search =
    request.nextUrl.search;

  const backendUrl =
    `${BACKEND_URL}${backendPath}${search}`;

  try {

    const headers =
      new Headers();

    const contentType =
      request.headers.get(
        "content-type"
      );

    const accept =
      request.headers.get(
        "accept"
      );

    if (contentType) {
      headers.set(
        "content-type",
        contentType
      );
    }

    if (accept) {
      headers.set(
        "accept",
        accept
      );
    }

    let body:
      | ArrayBuffer
      | undefined;

    if (
      request.method !==
        "GET" &&
      request.method !==
        "HEAD"
    ) {
      body =
        await request.arrayBuffer();
    }

    const response =
      await fetch(
        backendUrl,
        {
          method:
            request.method,

          headers,

          body,

          cache:
            "no-store",
        }
      );

    const responseBody =
      await response.arrayBuffer();

    const responseHeaders =
      new Headers();

    const responseContentType =
      response.headers.get(
        "content-type"
      );

    if (
      responseContentType
    ) {
      responseHeaders.set(
        "content-type",
        responseContentType
      );
    }

    return new NextResponse(
      responseBody,
      {
        status:
          response.status,

        headers:
          responseHeaders,
      }
    );

  } catch (error) {

    console.error(
      "EROI proxy error:",
      error
    );

    return NextResponse.json(
      {
        success: false,

        error:
          "Unable to connect to EROI FastAPI backend.",
      },
      {
        status: 502,
      }
    );
  }
}


export async function GET(
  request: NextRequest,
  context: {
    params: Promise<{
      path: string[];
    }>;
  }
) {

  const {
    path,
  } =
    await context.params;

  return proxyRequest(
    request,
    path
  );
}


export async function POST(
  request: NextRequest,
  context: {
    params: Promise<{
      path: string[];
    }>;
  }
) {

  const {
    path,
  } =
    await context.params;

  return proxyRequest(
    request,
    path
  );
}


export async function PUT(
  request: NextRequest,
  context: {
    params: Promise<{
      path: string[];
    }>;
  }
) {

  const {
    path,
  } =
    await context.params;

  return proxyRequest(
    request,
    path
  );
}


export async function PATCH(
  request: NextRequest,
  context: {
    params: Promise<{
      path: string[];
    }>;
  }
) {

  const {
    path,
  } =
    await context.params;

  return proxyRequest(
    request,
    path
  );
}


export async function DELETE(
  request: NextRequest,
  context: {
    params: Promise<{
      path: string[];
    }>;
  }
) {

  const {
    path,
  } =
    await context.params;

  return proxyRequest(
    request,
    path
  );
}
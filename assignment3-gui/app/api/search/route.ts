export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const query = searchParams.get('query');
  console.log(query)
  if (!query) {
    return new Response('Missing query parameter', { status: 400 });
  }
  return await fetch('http://127.0.0.1:5000/search?' + new URLSearchParams({query: query}))
}

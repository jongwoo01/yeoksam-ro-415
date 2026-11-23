export function onRequest({ request, next }) {
  const url = new URL(request.url);
  if (url.hostname === 'hanq-walk.leejongwoo.com') {
    url.hostname = 'yeoksamro415.leejongwoo.com';
    return Response.redirect(url.href, 301);
  }
  return next();
}

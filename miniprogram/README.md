# English Learning Mini Program

This directory is the WeChat Mini Program entry for the English learning app.

The current backend can be reused. Mini Program pages should call the same API
routes as the web app, with these identity headers on every request:

- `X-Client-Id`: anonymous client id stored in WeChat storage
- `X-Client-Source`: `wechat`
- `X-Client-Nickname`: optional nickname entered by the learner

## Local Setup

1. Open WeChat DevTools.
2. Import this `miniprogram` directory.
3. Fill in your Mini Program AppID, or use a test AppID for local debugging.
4. Update `globalData.apiBaseUrl` in `app.js`.

For production, the API base URL must be an HTTPS domain configured in the
WeChat Mini Program console as a valid request domain.


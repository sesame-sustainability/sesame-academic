import * as Sentry from "@sentry/browser";

type ClientRequestMethod = 'GET' | 'POST' | 'PUT' | 'PATCH'

export type Client = {
  body?: Record<string, unknown>;
  headers?: Record<string, string>;
  method?: ClientRequestMethod;
};

/**
 * Bare-metal impementation of client() to fetch from backend API
 * Does not send user Authentication header
 */
function client(
  endpoint: string,
  { body, headers = {}, method }: Client = {}
): Promise<Record<string, unknown> | object> {
  headers["Content-Type"] = "application/json";

  const config: {
    method: ClientRequestMethod;
    headers: Record<string, string>;
    body?: string;
  } = {
    method: method ?? (body ? "POST" : "GET"),
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  return window
    .fetch(`${process.env.API_URL}${endpoint}`, config)
    .then(async (response) => {
      const data = await response.json();

      if (response.ok) {
        return data;
      } else {
        // log timeouts to Sentry
        if (response.status === 504) {
          Sentry.captureEvent({
            message: `API request timed out`,
            transaction: 'timeout',
            extra: {
              endpoint,
              err: JSON.stringify(err),
            },
          });
        }
        return Promise.reject(data);
      }
    });
}

export default client;

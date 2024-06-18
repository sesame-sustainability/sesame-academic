// events.js

export const on = (eventType, listener) => {
  document.addEventListener(eventType, listener);
}

export const off = (eventType, listener) => {
  document.removeEventListener(eventType, listener);
}

export const once = (eventType, listener) => {
  on(eventType, handleEventOnce);

  function handleEventOnce(event) {
    listener(event);
    off(eventType, handleEventOnce);
  }
}

export const trigger = (eventType: string, data?: any) => {
  // console.log('triggering event of type:', eventType, 'with data:', data);
  const event = new CustomEvent(eventType, { detail: data });
  document.dispatchEvent(event);
}
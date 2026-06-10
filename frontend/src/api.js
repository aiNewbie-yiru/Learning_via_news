const CLIENT_ID_KEY = 'english_learning_client_id'
const NICKNAME_KEY = 'english_learning_nickname'

const randomPart = () => Math.random().toString(36).slice(2, 10)

export const getClientId = () => {
  let clientId = localStorage.getItem(CLIENT_ID_KEY)
  if (!clientId) {
    clientId = `web_${Date.now().toString(36)}_${randomPart()}`
    localStorage.setItem(CLIENT_ID_KEY, clientId)
  }
  return clientId
}

export const getClientNickname = () => localStorage.getItem(NICKNAME_KEY) || ''

export const setClientNickname = (nickname) => {
  const cleanNickname = (nickname || '').trim()
  if (cleanNickname) {
    localStorage.setItem(NICKNAME_KEY, cleanNickname)
  } else {
    localStorage.removeItem(NICKNAME_KEY)
  }
}

export const getIdentityHeaders = () => {
  const nickname = getClientNickname()
  return {
    'X-Client-Id': getClientId(),
    'X-Client-Source': 'web',
    ...(nickname ? { 'X-Client-Nickname': nickname } : {}),
  }
}

export const apiFetch = (url, options = {}) => {
  const headers = {
    ...getIdentityHeaders(),
    ...(options.headers || {}),
  }

  return fetch(url, {
    ...options,
    headers,
  })
}


const CLIENT_ID_KEY = 'english_learning_client_id'
const NICKNAME_KEY = 'english_learning_nickname'

const randomPart = () => Math.random().toString(36).slice(2, 10)

App({
  globalData: {
    apiBaseUrl: 'https://your-api-domain.example.com',
  },

  onLaunch() {
    this.ensureClientId()
  },

  ensureClientId() {
    let clientId = wx.getStorageSync(CLIENT_ID_KEY)
    if (!clientId) {
      clientId = `mp_${Date.now().toString(36)}_${randomPart()}`
      wx.setStorageSync(CLIENT_ID_KEY, clientId)
    }
    return clientId
  },

  getIdentityHeaders() {
    const nickname = wx.getStorageSync(NICKNAME_KEY)
    return {
      'X-Client-Id': this.ensureClientId(),
      'X-Client-Source': 'wechat',
      ...(nickname ? { 'X-Client-Nickname': nickname } : {}),
    }
  },

  setNickname(nickname) {
    const cleanNickname = (nickname || '').trim()
    if (cleanNickname) {
      wx.setStorageSync(NICKNAME_KEY, cleanNickname)
    } else {
      wx.removeStorageSync(NICKNAME_KEY)
    }
  },

  request({ url, method = 'GET', data }) {
    return new Promise((resolve, reject) => {
      wx.request({
        url: `${this.globalData.apiBaseUrl}${url}`,
        method,
        data,
        header: this.getIdentityHeaders(),
        success: (res) => {
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
          } else {
            reject(new Error(res.data?.detail || `Request failed: ${res.statusCode}`))
          }
        },
        fail: reject,
      })
    })
  },
})


const app = getApp()

Page({
  data: {
    articles: [],
    selectedArticle: null,
    loading: true,
    error: '',
  },

  onLoad() {
    this.loadTodayArticles()
  },

  async loadTodayArticles() {
    this.setData({ loading: true, error: '' })
    try {
      const articles = await app.request({ url: '/api/articles/compare?limit=5' })
      this.setData({
        articles,
        selectedArticle: articles && articles.length ? articles[0] : null,
      })
    } catch (error) {
      this.setData({ error: error.message || 'Failed to load articles' })
    } finally {
      this.setData({ loading: false })
    }
  },

  selectArticle(event) {
    const id = Number(event.currentTarget.dataset.id)
    const selectedArticle = this.data.articles.find((article) => article.id === id)
    this.setData({ selectedArticle })
  },
})


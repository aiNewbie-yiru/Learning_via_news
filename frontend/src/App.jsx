import React, { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import ArticleDetail from './pages/ArticleDetail'
import './App.css'

const ARTICLE_WINDOW_SIZE = 4

function App() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedArticle, setSelectedArticle] = useState(null)
  const [skippingId, setSkippingId] = useState(null)

  useEffect(() => {
    fetch(`/api/articles/compare?limit=${ARTICLE_WINDOW_SIZE}`)
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch articles')
        return res.json()
      })
      .then(data => {
        if (data && data.length > 0) {
          setArticles(data)
        } else {
          throw new Error('No articles available from compare')
        }
        setLoading(false)
      })
      .catch(err => {
        console.error('Fetch error:', err)
        fetch('/api/articles/today')
          .then(res => res.json())
          .then(data => {
            setArticles(data ? [data] : [])
            setLoading(false)
          })
          .catch(e => {
            setError(e.message)
            setLoading(false)
          })
      })
  }, [])

  const handleSelectArticle = (articleId) => {
    fetch('/api/articles/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ article_id: articleId, action: 'select' })
    })
    
    const article = articles.find(a => a.id === articleId)
    if (article) {
      setSelectedArticle(article)
    }
  }

  const handleSkipArticle = (articleId) => {
    const cursorId = articles[articles.length - 1]?.id
    setSkippingId(articleId)
    setTimeout(async () => {
      setArticles(prev => prev.filter(a => a.id !== articleId))
      setSkippingId(null)

      if (!cursorId) return

      try {
        const res = await fetch(`/api/articles/compare?skip_id=${cursorId}&limit=1`)
        if (!res.ok) return
        const data = await res.json()
        const nextArticle = data?.[0]
        if (!nextArticle) return

        setArticles(prev => {
          if (prev.some(article => article.id === nextArticle.id)) {
            return prev
          }
          return [...prev, nextArticle].slice(0, ARTICLE_WINDOW_SIZE)
        })
      } catch (err) {
        console.error('Failed to load replacement article:', err)
      }
    }, 300)
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading articles...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error">
        <h3>Error</h3>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={() => window.location.reload()}>Retry</button>
      </div>
    )
  }

  if (selectedArticle) {
    return <ArticleDetail article={selectedArticle} />
  }

  if (articles.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
            <circle cx="12" cy="7" r="4"></circle>
          </svg>
        </div>
        <h3>No articles available</h3>
        <p>Come back later for today's news!</p>
        <button className="btn btn-primary" onClick={() => window.location.reload()}>Refresh</button>
      </div>
    )
  }

  const getDifficultyClass = (level) => {
    if (!level) return 'cet6'
    if (typeof level === 'string') return level.toLowerCase()
    const levels = { 1: 'basic', 2: 'cet4', 3: 'cet6', 4: 'toefl', 5: 'gre' }
    return levels[level] || 'cet6'
  }

  const getDifficultyLabel = (level) => {
    if (!level) return 'Medium'
    if (typeof level === 'string') return level
    const labels = { 1: 'Basic', 2: 'CET4', 3: 'CET6', 4: 'TOEFL', 5: 'GRE' }
    return labels[level] || 'Medium'
  }

  return (
    <div className="article-selector">
      <div className="selector-header">
        <h2>Choose Today's Article</h2>
        <p className="selector-subtitle">Select an article that matches your skill level</p>
      </div>
      
      <div className="articles-grid">
        {articles.map((article) => (
          <div 
            key={article.id} 
            className={`article-select-card ${skippingId === article.id ? 'skipping' : ''}`}
          >
            <div className="article-card-hero">
              <div className="card-header-top">
                <span className="source-badge">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5m-1.414-9.414a2 2 0 1 1 2.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                  </svg>
                  {article.source}
                </span>
                <span className={`difficulty-badge ${getDifficultyClass(article.difficulty_level)}`}>
                  {getDifficultyLabel(article.difficulty_level)}
                </span>
              </div>
              <h3>{article.title}</h3>
            </div>
            
            <div className="article-card-body">
              <p className="excerpt">{article.content}</p>
              <div className="article-meta">
                <span>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2z"></path>
                  </svg>
                  {article.published_at?.split('T')[0]}
                </span>
                <span>
                  <a href={article.url} target="_blank" rel="noopener noreferrer">View Original</a>
                </span>
              </div>
              
              <div className="article-actions">
                <button 
                  className="btn-select"
                  onClick={() => handleSelectArticle(article.id)}
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="20 6 9 17 4 12"></polyline>
                  </svg>
                  Select
                </button>
                <button 
                  className="btn-skip"
                  onClick={() => handleSkipArticle(article.id)}
                  title="Skip this article"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App

import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { apiFetch } from '../api'

function ArticleList() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch('/api/articles')
      .then(res => res.json())
      .then(data => {
        setArticles(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching articles:', err)
        setLoading(false)
      })
  }, [])

  if (loading) return <div className="loading">Loading articles...</div>

  return (
    <div className="article-list">
      <h2>All Articles</h2>
      <div className="article-grid">
        {articles.map(article => (
          <Link to={`/articles/${article.id}`} key={article.id} className="article-card">
            <h3>{article.title}</h3>
            <p className="article-meta">
              {article.source} • {new Date(article.published_at).toLocaleDateString()}
            </p>
            {article.summary && <p className="article-summary">{article.summary.slice(0, 100)}...</p>}
          </Link>
        ))}
      </div>
      {articles.length === 0 && <p className="no-articles">No articles yet. Check back soon!</p>}
    </div>
  )
}

export default ArticleList

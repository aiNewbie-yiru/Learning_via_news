import React, { useState, useEffect } from 'react'

function Favorites() {
  const [words, setWords] = useState([])
  const [phrases, setPhrases] = useState([])
  const [activeTab, setActiveTab] = useState('words')
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/favorites/words')
      .then(res => res.json())
      .then(data => setWords(data))
    
    fetch('/api/favorites/phrases')
      .then(res => res.json())
      .then(data => setPhrases(data))
    
    fetch('/api/favorites/stats')
      .then(res => res.json())
      .then(data => setStats(data))
    
    setLoading(false)
  }, [])

  const handleRemoveWord = async (id, word) => {
    if (confirm(`Are you sure you want to remove "${word}" from favorites?`)) {
      await fetch(`/api/favorites/words/${id}`, { method: 'DELETE' })
      setWords(words.filter(w => w.id !== id))
      alert(`"${word}" removed from favorites`)
    }
  }

  const handleRemovePhrase = async (id, phrase) => {
    if (confirm(`Are you sure you want to remove "${phrase}" from favorites?`)) {
      await fetch(`/api/favorites/phrases/${id}`, { method: 'DELETE' })
      setPhrases(phrases.filter(p => p.id !== id))
      alert(`"${phrase}" removed from favorites`)
    }
  }

  if (loading) return <div className="loading">Loading favorites...</div>

  return (
    <div className="favorites-page">
      <h2>📖 My Word Book</h2>
      
      {stats && (
        <div className="stats-cards">
          <div className="stat-card">
            <div className="stat-number">{stats.word_count}</div>
            <div className="stat-label">Favorite Words</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.phrase_count}</div>
            <div className="stat-label">Favorite Phrases</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.total_items}</div>
            <div className="stat-label">Total Items</div>
          </div>
          <div className="stat-card">
            <div className="stat-number">{stats.total_reviews}</div>
            <div className="stat-label">Total Reviews</div>
          </div>
        </div>
      )}

      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'words' ? 'active' : ''}`}
          onClick={() => setActiveTab('words')}
        >
          Words ({words.length})
        </button>
        <button 
          className={`tab-btn ${activeTab === 'phrases' ? 'active' : ''}`}
          onClick={() => setActiveTab('phrases')}
        >
          Phrases ({phrases.length})
        </button>
      </div>

      {activeTab === 'words' && (
        <div className="word-list">
          {words.length === 0 ? (
            <div className="empty-state">
              <p>No favorite words yet.</p>
              <p>Start reading articles and add words to your word book!</p>
            </div>
          ) : (
            words.map(word => (
              <div key={word.id} className="word-card">
                <div className="word-header">
                  <span className="word-text">{word.word}</span>
                  <span className={`difficulty-badge ${word.difficulty_level.toLowerCase()}`}>
                    {word.difficulty_level}
                  </span>
                  {word.part_of_speech && (
                    <span className="pos-badge">{word.part_of_speech}</span>
                  )}
                </div>
                <p className="word-definition">{word.definition}</p>
                <p className="word-example">
                  <strong>Example:</strong> {word.example_sentence}
                </p>
                <p className="word-source">From: {word.article_title}</p>
                <p className="word-meta">
                  Added: {new Date(word.added_at).toLocaleDateString()} | 
                  Reviewed: {word.review_count} times
                </p>
                <button 
                  className="remove-btn"
                  onClick={() => handleRemoveWord(word.id, word.word)}
                >
                  Remove
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {activeTab === 'phrases' && (
        <div className="phrase-list">
          {phrases.length === 0 ? (
            <div className="empty-state">
              <p>No favorite phrases yet.</p>
              <p>Start reading articles and add phrases to your word book!</p>
            </div>
          ) : (
            phrases.map(phrase => (
              <div key={phrase.id} className="phrase-card">
                <div className="phrase-header">
                  <span className="phrase-text">{phrase.phrase}</span>
                </div>
                <p className="phrase-meaning">{phrase.meaning}</p>
                <p className="phrase-example">
                  <strong>Example:</strong> {phrase.example_sentence}
                </p>
                <p className="phrase-source">From: {phrase.article_title}</p>
                <p className="phrase-meta">
                  Added: {new Date(phrase.added_at).toLocaleDateString()} | 
                  Reviewed: {phrase.review_count} times
                </p>
                <button 
                  className="remove-btn"
                  onClick={() => handleRemovePhrase(phrase.id, phrase.phrase)}
                >
                  Remove
                </button>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  )
}

export default Favorites
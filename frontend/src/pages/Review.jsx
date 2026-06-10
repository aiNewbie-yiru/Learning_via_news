import React, { useState, useEffect } from 'react'
import { apiFetch } from '../api'

function Review() {
  const [reviewItems, setReviewItems] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [reviewType, setReviewType] = useState('all')
  const [reviewCount, setReviewCount] = useState(0)
  const [loading, setLoading] = useState(true)
  const [sessionStats, setSessionStats] = useState({ correct: 0, wrong: 0 })

  useEffect(() => {
    loadReviewItems()
  }, [reviewType])

  const loadReviewItems = async () => {
    setLoading(true)
    const response = await apiFetch(`/api/favorites/review?item_type=${reviewType}&limit=10`)
    const data = await response.json()
    setReviewItems(data)
    setCurrentIndex(0)
    setShowAnswer(false)
    setReviewCount(0)
    setSessionStats({ correct: 0, wrong: 0 })
    setLoading(false)
  }

  const handleRevealAnswer = () => {
    setShowAnswer(true)
  }

  const handleMarkReviewed = async (correct) => {
    const currentItem = reviewItems[currentIndex]
    await apiFetch(`/api/favorites/review/${currentItem.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_type: currentItem.type })
    })

    setSessionStats(prev => ({
      correct: prev.correct + (correct ? 1 : 0),
      wrong: prev.wrong + (correct ? 0 : 1)
    }))

    setReviewCount(prev => prev + 1)

    if (currentIndex < reviewItems.length - 1) {
      setCurrentIndex(prev => prev + 1)
      setShowAnswer(false)
    }
  }

  const handleSkip = () => {
    if (currentIndex < reviewItems.length - 1) {
      setCurrentIndex(prev => prev + 1)
      setShowAnswer(false)
    }
  }

  const handleRestart = () => {
    loadReviewItems()
  }

  if (loading) return <div className="loading">Loading review items...</div>

  if (reviewItems.length === 0) {
    return (
      <div className="empty-state">
        <h2>🔄 Review Session</h2>
        <p>No items to review. Add some words or phrases to your word book first!</p>
      </div>
    )
  }

  const currentItem = reviewItems[currentIndex]
  const progress = ((currentIndex + 1) / reviewItems.length) * 100

  if (reviewCount >= reviewItems.length) {
    const accuracy = sessionStats.correct + sessionStats.wrong > 0
      ? Math.round((sessionStats.correct / (sessionStats.correct + sessionStats.wrong)) * 100)
      : 0

    return (
      <div className="review-complete">
        <h2>🎉 Review Complete!</h2>
        <div className="completion-stats">
          <div className="completion-stat">
            <div className="completion-number">{sessionStats.correct}</div>
            <div className="completion-label">Correct</div>
          </div>
          <div className="completion-stat">
            <div className="completion-number">{sessionStats.wrong}</div>
            <div className="completion-label">Wrong</div>
          </div>
          <div className="completion-stat">
            <div className="completion-number">{accuracy}%</div>
            <div className="completion-label">Accuracy</div>
          </div>
        </div>
        <button className="restart-btn" onClick={handleRestart}>
          🔄 Start New Review
        </button>
      </div>
    )
  }

  return (
    <div className="review-page">
      <h2>🔄 Review Session</h2>
      
      <div className="review-controls">
        <select 
          value={reviewType} 
          onChange={(e) => setReviewType(e.target.value)}
          className="review-type-select"
        >
          <option value="all">All Items</option>
          <option value="words">Words Only</option>
          <option value="phrases">Phrases Only</option>
        </select>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }}></div>
      </div>
      <p className="progress-text">{currentIndex + 1} / {reviewItems.length}</p>

      <div className="review-card">
        <div className="item-type-badge">
          {currentItem.type === 'word' ? '📝 Word' : '💬 Phrase'}
        </div>
        
        <h3 className="item-text">{currentItem.item}</h3>
        
        {!showAnswer ? (
          <div className="answer-hidden">
            <p>Click "Reveal Answer" to see the definition</p>
            <button className="reveal-btn" onClick={handleRevealAnswer}>
              👁️ Reveal Answer
            </button>
          </div>
        ) : (
          <div className="answer-shown">
            <div className="definition-section">
              <h4>Definition:</h4>
              <p>{currentItem.definition}</p>
            </div>
            <div className="example-section">
              <h4>Example Sentence:</h4>
              <p>"{currentItem.example_sentence}"</p>
            </div>
            {currentItem.difficulty_level && (
              <div className="difficulty-section">
                <span className={`difficulty-badge ${currentItem.difficulty_level.toLowerCase()}`}>
                  {currentItem.difficulty_level}
                </span>
              </div>
            )}
            <div className="action-buttons">
              <button className="correct-btn" onClick={() => handleMarkReviewed(true)}>
                ✅ I Know It
              </button>
              <button className="wrong-btn" onClick={() => handleMarkReviewed(false)}>
                ❌ Need More Practice
              </button>
              <button className="skip-btn" onClick={handleSkip}>
                ⏭️ Skip
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="session-stats">
        <span>Correct: {sessionStats.correct}</span>
        <span>Wrong: {sessionStats.wrong}</span>
      </div>
    </div>
  )
}

export default Review

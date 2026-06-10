import React, { useState, useEffect } from 'react'
import { apiFetch, getClientNickname, setClientNickname } from '../api'

function CommentsSection({ articleId }) {
  const [comments, setComments] = useState([])
  const [newComment, setNewComment] = useState('')
  const [userName, setUserName] = useState(getClientNickname())
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchComments()
  }, [articleId])

  const fetchComments = async () => {
    try {
      const res = await apiFetch(`/api/comments/article/${articleId}`)
      const data = await res.json()
      setComments(data)
    } catch (err) {
      console.error('Error fetching comments:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!newComment.trim()) return

    setSubmitting(true)
    try {
      if (userName.trim()) {
        setClientNickname(userName)
      }

      const res = await apiFetch('/api/comments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          article_id: articleId,
          content: newComment,
          user_name: userName
        })
      })
      const data = await res.json()
      setComments([...comments, data])
      setNewComment('')
    } catch (err) {
      console.error('Error submitting comment:', err)
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) return <div className="loading">Loading comments...</div>

  return (
    <div className="comments-section">
      <h3>💬 Discussion & AI Chat</h3>
      <p className="chat-intro">
        Share your thoughts about this article! Our AI learning assistant will respond to help you practice English.
      </p>

      <div className="comments-list">
        {comments.length === 0 ? (
          <p className="no-comments">Be the first to share your thoughts!</p>
        ) : (
          comments.map(comment => (
            <div key={comment.id} className="comment">
              <div className="comment-user">
                <span className="user-name">{comment.user_name}</span>
                <span className="comment-time">
                  {new Date(comment.created_at).toLocaleString()}
                </span>
              </div>
              <p className="comment-content">{comment.content}</p>

              {comment.ai_response && (
                <div className="ai-response">
                  <span className="ai-label">🤖 AI Tutor:</span>
                  <p>{comment.ai_response}</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSubmit} className="comment-form">
        <input
          type="text"
          placeholder="Your name (optional)"
          value={userName}
          onChange={(e) => setUserName(e.target.value)}
          className="name-input"
        />
        <textarea
          placeholder="Share your thoughts about this article..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          className="comment-input"
          rows={3}
        />
        <button type="submit" disabled={submitting || !newComment.trim()}>
          {submitting ? 'Sending...' : 'Submit & Get AI Response'}
        </button>
      </form>
    </div>
  )
}

export default CommentsSection

import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import CommentsSection from '../components/CommentsSection'
import { apiFetch } from '../api'

function ArticleDetail({ article: propArticle }) {
    const { id } = useParams()
    const [article, setArticle] = useState(propArticle)
    const [loading, setLoading] = useState(!propArticle)
    const [activeTab, setActiveTab] = useState('words')
    const [favoritedWords, setFavoritedWords] = useState(new Set())
    const [favoritedPhrases, setFavoritedPhrases] = useState(new Set())

    useEffect(() => {
        if (!propArticle && id) {
            apiFetch(`/api/articles/${id}`)
                .then(res => res.json())
                .then(data => {
                    setArticle(data)
                    setLoading(false)
                })
                .catch(err => {
                    console.error('Error fetching article:', err)
                    setLoading(false)
                })
        }
        loadFavorites()
    }, [id, propArticle])

    const loadFavorites = async () => {
        const [wordsRes, phrasesRes] = await Promise.all([
            apiFetch('/api/favorites/words'),
            apiFetch('/api/favorites/phrases')
        ])
        const words = await wordsRes.json()
        const phrases = await phrasesRes.json()
        setFavoritedWords(new Set(words.map(w => w.word)))
        setFavoritedPhrases(new Set(phrases.map(p => p.phrase)))
    }

    const handleFavoriteWord = async (wordId, wordText) => {
        if (favoritedWords.has(wordText)) {
            const favWord = await apiFetch('/api/favorites/words').then(r => r.json())
            const toRemove = favWord.find(w => w.word === wordText)
            if (toRemove) {
                await apiFetch(`/api/favorites/words/${toRemove.id}`, { method: 'DELETE' })
                setFavoritedWords(prev => {
                    const next = new Set(prev)
                    next.delete(wordText)
                    return next
                })
            }
        } else {
            await apiFetch(`/api/favorites/words/${wordId}`, { method: 'POST' })
            setFavoritedWords(prev => new Set([...prev, wordText]))
        }
    }

    const handleFavoritePhrase = async (phraseId, phraseText) => {
        if (favoritedPhrases.has(phraseText)) {
            const favPhrases = await apiFetch('/api/favorites/phrases').then(r => r.json())
            const toRemove = favPhrases.find(p => p.phrase === phraseText)
            if (toRemove) {
                await apiFetch(`/api/favorites/phrases/${toRemove.id}`, { method: 'DELETE' })
                setFavoritedPhrases(prev => {
                    const next = new Set(prev)
                    next.delete(phraseText)
                    return next
                })
            }
        } else {
            await apiFetch(`/api/favorites/phrases/${phraseId}`, { method: 'POST' })
            setFavoritedPhrases(prev => new Set([...prev, phraseText]))
        }
    }

    const getDifficultyClass = (level) => {
        if (!level) return 'cet6'
        const levels = { 'basic': 'basic', 'CET4': 'cet4', 'CET6': 'cet6', 'TOEFL': 'toefl', 'GRE': 'gre' }
        return levels[level] || 'cet6'
    }

    if (loading) return <div className="loading"><div className="loading-spinner"></div><div className="loading-text">Loading article...</div></div>
    if (!article) return <div className="error"><h3>Article not found</h3><p>The article you're looking for doesn't exist.</p><button onClick={() => window.history.back()}>Go back</button></div>

    const handleHideWord = async (wordId) => {
        await apiFetch(`/api/articles/words/${wordId}/hide`, { method: 'POST' })
        setArticle(prev => ({
            ...prev,
            words: prev.words.filter(w => w.id !== wordId)
        }))
    }

    const handleHidePhrase = async (phraseId) => {
        await apiFetch(`/api/articles/phrases/${phraseId}/hide`, { method: 'POST' })
        setArticle(prev => ({
            ...prev,
            phrases: prev.phrases.filter(p => p.id !== phraseId)
        }))
    }

    return (
        <div className="article-detail">
            <article className="article-content">
                <div className="article-detail-header">
                    <div className="header-top">
                        <span className="source-badge">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M11 5H6a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-5m-1.414-9.414a2 2 0 1 1 2.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                            {article.source}
                        </span>
                        <span className={`difficulty-badge ${getDifficultyClass(article.difficulty_level)}`}>
                            {article.difficulty_level || 'CET6'}
                        </span>
                    </div>
                    <h1>{article.title}</h1>
                    <div className="meta">
                        <span>{new Date(article.published_at).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                        <a href={article.url} target="_blank" rel="noopener noreferrer">View Original</a>
                    </div>
                </div>
                <div className="article-body">
                    <div className="article-text">
                        {article.content.split('\n').map((paragraph, index) => (
                            <p key={index}>{paragraph}</p>
                        ))}
                    </div>
                </div>

                <div className="comments-section">
                    <h3>💬 Discussion</h3>
                    <p className="chat-intro">Share your thoughts about this article and get AI responses!</p>
                    <CommentsSection key={article.id} articleId={article.id} />
                </div>
            </article>

            <section className="vocabulary-section">
                <div className="vocab-tabs">
                    <button
                        className={`vocab-tab ${activeTab === 'words' ? 'active' : ''}`}
                        onClick={() => setActiveTab('words')}
                    >
                        Words ({article.words?.length || 0})
                    </button>
                    <button
                        className={`vocab-tab ${activeTab === 'phrases' ? 'active' : ''}`}
                        onClick={() => setActiveTab('phrases')}
                    >
                        Phrases ({article.phrases?.length || 0})
                    </button>
                </div>

                <div className="vocab-tab-content">
                    {activeTab === 'words' && (
                        <div className="words-list">
                            {article.words && article.words.length > 0 ? (
                                article.words.map(word => (
                                    <div key={word.id} className="word-card">
                                        <div className="word-header">
                                            <div className="word-main">
                                                <span className="word-text">{word.word}</span>
                                                {word.pronunciation && (
                                                    <span className="word-pronunciation">/{word.pronunciation}/</span>
                                                )}
                                            </div>
                                            <button
                                                className={`favorite-btn ${favoritedWords.has(word.word) ? 'favorited' : ''}`}
                                                onClick={() => handleFavoriteWord(word.id, word.word)}
                                                title={favoritedWords.has(word.word) ? 'Remove from favorites' : 'Add to favorites'}
                                            >
                                                <svg viewBox="0 0 24 24" fill={favoritedWords.has(word.word) ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
                                                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                                                </svg>
                                            </button>
                                            <button
                                                className="hide-btn"
                                                onClick={() => handleHideWord(word.id)}
                                                title="Hide this word"
                                            >
                                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <line x1="18" y1="6" x2="6" y2="18"></line>
                                                    <line x1="6" y1="6" x2="18" y2="18"></line>
                                                </svg>
                                            </button>
                                        </div>
                                        <div className="word-tags">
                                            <span className={`difficulty-badge ${getDifficultyClass(word.difficulty_level)}`}>
                                                {word.difficulty_level || 'CET6'}
                                            </span>
                                            {word.part_of_speech && (
                                                <span className="pos-badge">{word.part_of_speech}</span>
                                            )}
                                        </div>
                                        {word.definition && (
                                            <div className="word-definition-block">
                                                <h4 className="section-title">📖 Definition</h4>
                                                <p className="word-definition">{word.definition}</p>
                                                {word.definition_cn && (
                                                    <p className="word-definition-cn">{word.definition_cn}</p>
                                                )}
                                            </div>
                                        )}
                                        {word.example_sentence && (
                                            <div className="word-example">
                                                <h4 className="section-title">💡 Example</h4>
                                                <p className="example-sentence">{word.example_sentence}</p>
                                                {word.example_cn && (
                                                    <p className="example-cn">{word.example_cn}</p>
                                                )}
                                                {word.example_source && (
                                                    <span className="example-source">{word.example_source}</span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="no-content">
                                    <p>No vocabulary extracted yet.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'phrases' && (
                        <div className="phrases-list">
                            {article.phrases && article.phrases.length > 0 ? (
                                article.phrases.map(phrase => (
                                    <div key={phrase.id} className="phrase-card">
                                        <div className="phrase-header">
                                            <span className="phrase-text">{phrase.phrase}</span>
                                            <button
                                                className={`favorite-btn ${favoritedPhrases.has(phrase.phrase) ? 'favorited' : ''}`}
                                                onClick={() => handleFavoritePhrase(phrase.id, phrase.phrase)}
                                                title={favoritedPhrases.has(phrase.phrase) ? 'Remove from favorites' : 'Add to favorites'}
                                            >
                                                <svg viewBox="0 0 24 24" fill={favoritedPhrases.has(phrase.phrase) ? 'currentColor' : 'none'} stroke="currentColor" strokeWidth="2">
                                                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                                                </svg>
                                            </button>
                                            <button
                                                className="hide-btn"
                                                onClick={() => handleHidePhrase(phrase.id)}
                                                title="Hide this phrase"
                                            >
                                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                                    <line x1="18" y1="6" x2="6" y2="18"></line>
                                                    <line x1="6" y1="6" x2="18" y2="18"></line>
                                                </svg>
                                            </button>
                                        </div>
                                        {phrase.meaning && (
                                            <div className="phrase-meaning-block">
                                                <h4 className="section-title">📖 Meaning</h4>
                                                <p className="phrase-meaning">{phrase.meaning}</p>
                                                {phrase.meaning_cn && (
                                                    <p className="phrase-meaning-cn">{phrase.meaning_cn}</p>
                                                )}
                                            </div>
                                        )}
                                        {phrase.example_sentence && (
                                            <div className="phrase-example">
                                                <h4 className="section-title">💡 Example</h4>
                                                <p className="example-sentence">{phrase.example_sentence}</p>
                                                {phrase.example_cn && (
                                                    <p className="example-cn">{phrase.example_cn}</p>
                                                )}
                                                {phrase.example_source && (
                                                    <span className="example-source">{phrase.example_source}</span>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                ))
                            ) : (
                                <div className="no-content">
                                    <p>No phrases or idioms extracted yet.</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </section>
        </div>
    )
}

export default ArticleDetail

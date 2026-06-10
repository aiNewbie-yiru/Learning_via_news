import React, { useState, useEffect } from 'react'
import CommentsSection from './components/CommentsSection'
import Favorites from './pages/Favorites'
import { apiFetch } from './api'
import './App.css'

const TODAY_ARTICLE_LIMIT = 5

const LOOKUP_SKIP_WORDS = new Set([
  'the', 'a', 'an', 'and', 'or', 'but', 'if', 'because', 'so', 'than', 'as',
  'to', 'of', 'in', 'on', 'at', 'by', 'for', 'from', 'with', 'about', 'into',
  'over', 'after', 'before', 'between', 'through', 'during', 'under', 'above',
  'below', 'up', 'down', 'out', 'off',
  'i', 'me', 'my', 'mine', 'you', 'your', 'yours', 'he', 'him', 'his', 'she',
  'her', 'hers', 'it', 'its', 'we', 'us', 'our', 'ours', 'they', 'them',
  'their', 'theirs', 'this', 'that', 'these', 'those', 'who', 'whom', 'whose',
  'which', 'what', 'where', 'when', 'why', 'how',
  'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being', 'do', 'does', 'did',
  'done', 'have', 'has', 'had', 'having', 'will', 'would', 'shall', 'should',
  'can', 'could', 'may', 'might', 'must',
  'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
  'now', 'not', 'no', 'yes', 'very', 'just', 'also', 'only', 'all', 'some',
  'any', 'each', 'every', 'more', 'most', 'many', 'much', 'such', 'other'
])

const POS_CLASS_MAP = [
  { matches: ['noun', 'n.'], className: 'noun' },
  { matches: ['verb', 'v.'], className: 'verb' },
  { matches: ['adjective', 'adj.'], className: 'adjective' },
  { matches: ['adverb', 'adv.'], className: 'adverb' }
]

const normalizeWord = (value) => (value || '').toLowerCase().replace(/^[^a-z]+|[^a-z]+$/g, '')

const isLookupCandidate = (token) => {
  const normalized = normalizeWord(token)
  if (normalized.length < 3) return false
  if (LOOKUP_SKIP_WORDS.has(normalized)) return false
  if (/^[A-Z]{2,}$/.test(token)) return false
  if (token.includes("'")) return false
  return true
}

const getPartOfSpeechClass = (partOfSpeech) => {
  const normalized = (partOfSpeech || '').toLowerCase()
  const matched = POS_CLASS_MAP.find(item => item.matches.some(pos => normalized.includes(pos)))
  return matched?.className || 'other'
}

const compactChineseMeaning = (value) => (value || '')
  .replace(/^\s*(原文义|语境义|常用义|中文释义|释义|意思|含义)[:：]\s*/i, '')
  .replace(/\s+/g, '')
  .trim()

const getDisplayDefinitionCn = (word) => {
  const contextMeaning = compactChineseMeaning(word.context_definition_cn)
  const commonMeaning = compactChineseMeaning(word.common_definition_cn)

  if (contextMeaning && commonMeaning && contextMeaning !== commonMeaning) {
    return `${contextMeaning}；${commonMeaning}`
  }

  return contextMeaning || commonMeaning || compactChineseMeaning(word.definition_cn)
}

const getContextMeaningCn = (word) => compactChineseMeaning(word.context_definition_cn)

const getCommonMeaningCn = (word) => compactChineseMeaning(word.common_definition_cn)

const splitDefinitionCandidates = (definitionCn) => {
  if (!definitionCn) return []
  return definitionCn
    .split(/[;；。.\n,，、]/)
    .map(item => item.replace(/^\s*(中文释义|释义|意思|含义)[:：]\s*/i, '').trim())
    .map(item => item.replace(/^[0-9一二三四五六七八九十]+[.)、]\s*/, '').trim())
    .filter(Boolean)
}

const trimGloss = (value) => {
  if (!value) return ''
  const cleaned = value
    .replace(/\([^)]*\)/g, '')
    .replace(/（[^）]*）/g, '')
    .replace(/\s+/g, '')
    .trim()

  if (cleaned.length <= 8) return cleaned
  return cleaned.slice(0, 8)
}

const getInlineWordGloss = (word) => {
  return trimGloss(compactChineseMeaning(word.context_definition_cn))
}

const getInlinePhraseGloss = (phrase) => {
  return trimGloss(compactChineseMeaning(phrase.meaning_cn))
}

const buildWordLookup = (words = []) => {
  const lookup = new Map()

  words.forEach(word => {
    const base = normalizeWord(word.word)
    if (!base) return

    const forms = new Set([base])
    if (base.endsWith('y')) forms.add(`${base.slice(0, -1)}ies`)
    if (base.endsWith('e')) {
      forms.add(`${base}d`)
      forms.add(`${base.slice(0, -1)}ing`)
    } else {
      forms.add(`${base}ed`)
      forms.add(`${base}ing`)
    }
    forms.add(`${base}s`)
    forms.add(`${base}es`)

    forms.forEach(form => {
      if (!lookup.has(form)) lookup.set(form, word)
    })
  })

  return lookup
}

const buildPhraseMatchers = (phrases = []) => {
  return phrases
    .map(phrase => {
      const text = (phrase.phrase || '').trim()
      const gloss = getInlinePhraseGloss(phrase)
      if (!text || text.split(/\s+/).length < 2) return null

      const pattern = new RegExp(
        `^${text.split(/\s+/).map(part => part.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('\\s+')}(?![A-Za-z])`,
        'i'
      )

      return { phrase, text, gloss, pattern }
    })
    .filter(Boolean)
    .sort((a, b) => b.text.length - a.text.length)
}

const renderAnnotatedParagraph = (
  paragraph,
  words,
  phrases,
  onWordClick,
  activeWordId,
  onLookupWord,
  lookupWord,
  options = {}
) => {
  const showGloss = options.showGloss !== false
  const wordLookup = buildWordLookup(words)
  const phraseMatchers = buildPhraseMatchers(phrases)
  const nodes = []
  let cursor = 0
  let nodeIndex = 0

  while (cursor < paragraph.length) {
    const rest = paragraph.slice(cursor)

    if (!/^[A-Za-z]/.test(rest)) {
      const nextWordIndex = rest.search(/[A-Za-z]/)
      if (nextWordIndex === -1) {
        nodes.push(rest)
        break
      }
      nodes.push(rest.slice(0, nextWordIndex))
      cursor += nextWordIndex
      continue
    }

    const phraseMatch = phraseMatchers.find(item => item.pattern.test(rest))
    if (phraseMatch) {
      const original = rest.match(phraseMatch.pattern)[0]
      if (showGloss && phraseMatch.gloss) {
        nodes.push(
          <button
            key={`phrase-${phraseMatch.phrase.id || phraseMatch.text}-${nodeIndex}`}
            type="button"
            className="annotated-word annotated-phrase pos-other"
            title="Phrase"
          >
            <span className="annotated-original">{original}</span>
            <span className="annotated-gloss">{phraseMatch.gloss}</span>
          </button>
        )
      } else {
        nodes.push(original)
      }
      cursor += original.length
      nodeIndex += 1
      continue
    }

    const wordMatch = rest.match(/^[A-Za-z][A-Za-z'-]*/)
    if (!wordMatch) {
      nodes.push(paragraph[cursor])
      cursor += 1
      continue
    }

    const token = wordMatch[0]
    const normalized = normalizeWord(token)
    const matchedWord = normalized ? wordLookup.get(normalized) : null

    if (!matchedWord) {
      if (onLookupWord && isLookupCandidate(token)) {
        nodes.push(
          <button
            key={`lookup-${normalized}-${nodeIndex}`}
            type="button"
            className={`lookup-word ${lookupWord === normalized ? 'loading' : ''}`}
            onClick={(event) => onLookupWord(token, event)}
            title="Click to look up this word"
          >
            {token}
          </button>
        )
      } else {
        nodes.push(token)
      }
      cursor += token.length
      nodeIndex += 1
      continue
    }

    const gloss = showGloss ? getInlineWordGloss(matchedWord) : ''
    if (!gloss && !onLookupWord) {
      nodes.push(token)
      cursor += token.length
      continue
    }

    const posClass = getPartOfSpeechClass(matchedWord.part_of_speech)

    nodes.push(
      <button
        key={`${matchedWord.id}-${nodeIndex}`}
        type="button"
        className={`annotated-word pos-${posClass} ${gloss ? '' : 'no-gloss'} ${activeWordId === matchedWord.id ? 'active' : ''}`}
        onClick={(event) => onWordClick(token, matchedWord, event)}
        title="View word meaning"
      >
        <span className="annotated-original">{token}</span>
        {gloss && <span className="annotated-gloss">{gloss}</span>}
      </button>
    )
    cursor += token.length
    nodeIndex += 1
  }

  return nodes
}

const getLookupPopoverPosition = (target) => {
  if (!target) return { top: 120, left: window.innerWidth / 2, placement: 'above' }

  const rect = target.getBoundingClientRect()
  const left = Math.min(Math.max(rect.left + rect.width / 2, 96), window.innerWidth - 96)
  const hasRoomAbove = rect.top > 96

  return {
    left,
    top: hasRoomAbove ? rect.top - 8 : rect.bottom + 8,
    placement: hasRoomAbove ? 'above' : 'below'
  }
}

function App() {
  const [articles, setArticles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedArticleId, setSelectedArticleId] = useState(null)
  const [activeTab, setActiveTab] = useState('words')
  const [activeView, setActiveView] = useState('today')
  const [favoritedWords, setFavoritedWords] = useState(new Set())
  const [favoritedPhrases, setFavoritedPhrases] = useState(new Set())
  const [activeWordId, setActiveWordId] = useState(null)
  const [lookupPanel, setLookupPanel] = useState({
    word: '',
    state: 'idle',
    message: '',
    data: null,
    top: 0,
    left: 0,
    placement: 'above'
  })

  useEffect(() => {
    loadTodayArticles()
    loadFavorites()
  }, [])

  useEffect(() => {
    if (lookupPanel.state === 'idle') return

    const closeLookupPanel = (event) => {
      if (
        event.target.closest('.lookup-popover') ||
        event.target.closest('.lookup-word') ||
        event.target.closest('.annotated-word')
      ) {
        return
      }

      setLookupPanel(prev => ({ ...prev, state: 'idle', message: '', data: null }))
    }

    document.addEventListener('mousedown', closeLookupPanel)
    return () => document.removeEventListener('mousedown', closeLookupPanel)
  }, [lookupPanel.state])

  const loadTodayArticles = async () => {
    try {
      const res = await apiFetch(`/api/articles/compare?limit=${TODAY_ARTICLE_LIMIT}`)
      if (!res.ok) throw new Error('Failed to fetch today articles')
      const data = await res.json()
      if (!data || data.length === 0) throw new Error('No articles available for today')
      setArticles(data)
      setSelectedArticleId(data[0].id)
    } catch (err) {
      console.error('Fetch error:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const loadFavorites = async () => {
    try {
      const [wordsRes, phrasesRes] = await Promise.all([
        apiFetch('/api/favorites/words'),
        apiFetch('/api/favorites/phrases')
      ])
      const words = await wordsRes.json()
      const phrases = await phrasesRes.json()
      setFavoritedWords(new Set(words.map(w => w.word)))
      setFavoritedPhrases(new Set(phrases.map(p => p.phrase)))
    } catch (err) {
      console.error('Error loading favorites:', err)
    }
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
      return
    }

    await apiFetch(`/api/favorites/words/${wordId}`, { method: 'POST' })
    setFavoritedWords(prev => new Set([...prev, wordText]))
  }

  const handleHideWord = async (wordId, wordText) => {
    await apiFetch(`/api/articles/words/${wordId}/hide`, { method: 'POST' })
    setArticles(prev => prev.map(article => ({
      ...article,
      words: (article.words || []).filter(word => word.word !== wordText)
    })))
    if (activeWordId === wordId) setActiveWordId(null)
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
      return
    }

    await apiFetch(`/api/favorites/phrases/${phraseId}`, { method: 'POST' })
    setFavoritedPhrases(prev => new Set([...prev, phraseText]))
  }

  const handleHidePhrase = async (phraseId, phraseText) => {
    await apiFetch(`/api/articles/phrases/${phraseId}/hide`, { method: 'POST' })
    setArticles(prev => prev.map(article => ({
      ...article,
      phrases: (article.phrases || []).filter(phrase => phrase.phrase !== phraseText)
    })))
  }

  const getDifficultyClass = (level) => {
    if (!level) return 'cet6'
    if (typeof level === 'string') return level.toLowerCase()
    const levels = { 1: 'basic', 2: 'cet4', 3: 'cet6', 4: 'toefl', 5: 'gre' }
    return levels[level] || 'cet6'
  }

  const getTopicLabel = (article) => {
    if (article.topic_label) return article.topic_label
    return article.title.split(/\s+/).slice(0, 3).join(' ')
  }

  const handleAnnotatedWordClick = (wordId) => {
    setActiveTab('words')
    setActiveWordId(wordId)
    window.setTimeout(() => {
      document.getElementById(`word-card-${wordId}`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }, 0)
  }

  const handleKnownWordClick = (rawWord, word, event) => {
    event?.stopPropagation()
    const wordId = word.id || word.word_id
    const position = getLookupPopoverPosition(event?.currentTarget)
    setLookupPanel({
      word: normalizeWord(rawWord || word.word),
      state: 'success',
      message: '',
      data: {
        ...word,
        word_id: wordId,
        in_word_list: true
      },
      ...position
    })
    if (wordId) setActiveWordId(wordId)
  }

  const handleLookupWord = async (rawWord, event) => {
    event?.stopPropagation()
    const normalized = normalizeWord(rawWord)
    if (!selectedArticle || !normalized) return

    const existingWord = buildWordLookup(selectedArticle.words || []).get(normalized)
    if (existingWord) {
      handleKnownWordClick(rawWord, existingWord, event)
      return
    }

    const position = getLookupPopoverPosition(event?.currentTarget)
    setLookupPanel({
      word: normalized,
      state: 'loading',
      message: '查词中...',
      data: null,
      ...position
    })

    try {
      const response = await apiFetch(`/api/articles/${selectedArticle.id}/lookup-word`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word: rawWord })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(errorText || 'Lookup failed')
      }

      const lookedUpWord = await response.json()
      if (lookedUpWord.in_word_list && lookedUpWord.word_id) {
        setActiveWordId(lookedUpWord.word_id)
      }
      setLookupPanel({
        word: normalized,
        state: 'success',
        message: '',
        data: lookedUpWord,
        ...position
      })
    } catch (err) {
      console.error('Lookup word error:', err)
      setLookupPanel({
        word: normalized,
        state: 'error',
        message: '暂时查不到释义',
        data: null,
        ...position
      })
    }
  }

  const handleAddLookupToWords = async (event) => {
    event?.stopPropagation()
    const lookup = lookupPanel.data
    if (!selectedArticle || !lookup?.word) return

    if (lookup.in_word_list && (lookup.word_id || lookup.id)) {
      return
    }

    setActiveTab('words')
    setLookupPanel(prev => ({
      ...prev,
      state: 'adding',
      message: '加入中...'
    }))

    try {
      const response = await apiFetch(`/api/articles/${selectedArticle.id}/add-word`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ word: lookup.word })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(errorText || 'Add word failed')
      }

      const addedWord = await response.json()
      setArticles(prev => prev.map(article => {
        if (article.id !== selectedArticle.id) return article

        const currentWords = article.words || []
        const nextWords = currentWords.some(word => word.id === addedWord.id || normalizeWord(word.word) === normalizeWord(addedWord.word))
          ? currentWords.map(word => (
              word.id === addedWord.id || normalizeWord(word.word) === normalizeWord(addedWord.word)
                ? addedWord
                : word
            ))
          : [addedWord, ...currentWords]

        return { ...article, words: nextWords }
      }))

      setActiveWordId(addedWord.id)
      setLookupPanel({
        word: normalizeWord(addedWord.word),
        state: 'success',
        message: '',
        data: {
          ...addedWord,
          word_id: addedWord.id,
          in_word_list: true
        },
        top: lookupPanel.top,
        left: lookupPanel.left,
        placement: lookupPanel.placement
      })
      window.setTimeout(() => {
        document.getElementById(`word-card-${addedWord.id}`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }, 0)
    } catch (err) {
      console.error('Add lookup word error:', err)
      setLookupPanel(prev => ({
        ...prev,
        state: 'error',
        message: '加入失败'
      }))
    }
  }

  const handleFavoriteLookupWord = async (event) => {
    event?.stopPropagation()
    const lookup = lookupPanel.data
    if (!selectedArticle || !lookup?.word || favoritedWords.has(lookup.word)) return

    try {
      if (lookup.in_word_list && (lookup.word_id || lookup.id)) {
        await apiFetch(`/api/favorites/words/${lookup.word_id || lookup.id}`, { method: 'POST' })
      } else {
        await apiFetch('/api/favorites/lookup-word', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ article_id: selectedArticle.id, word: lookup.word })
        })
      }

      setFavoritedWords(prev => new Set([...prev, lookup.word]))
      setLookupPanel(prev => ({
        ...prev,
        state: 'success',
        message: ''
      }))
    } catch (err) {
      console.error('Favorite lookup word error:', err)
      setLookupPanel(prev => ({
        ...prev,
        state: 'error',
        message: '收藏失败'
      }))
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        <div className="loading-text">Loading today's learning page...</div>
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

  const selectedArticle = articles.find(article => article.id === selectedArticleId) || articles[0]

  if (!selectedArticle) {
    return (
      <div className="empty-state">
        <h3>No articles available</h3>
        <p>Come back later for today's news.</p>
      </div>
    )
  }

  return (
    <div className="today-learning-page">
      <section className="topic-strip" aria-label="Today's topics">
        <div className="topic-strip-header">
          <span>Today's Articles</span>
          <div className="view-switcher" aria-label="Learning views">
            <button
              type="button"
              className={`view-switcher-btn ${activeView === 'today' ? 'active' : ''}`}
              onClick={() => setActiveView('today')}
            >
              Today
            </button>
            <button
              type="button"
              className={`view-switcher-btn ${activeView === 'favorites' ? 'active' : ''}`}
              onClick={() => setActiveView('favorites')}
            >
              Favorite Words
            </button>
          </div>
        </div>
        {activeView === 'today' && (
          <div className="topic-tabs">
            {articles.map(article => (
              <button
                key={article.id}
                className={`topic-tab ${article.id === selectedArticle.id ? 'active' : ''}`}
                onClick={() => {
                  setSelectedArticleId(article.id)
                  setActiveTab('words')
                  setActiveWordId(null)
                }}
              >
                <span className="topic-en">{getTopicLabel(article)}</span>
                <span className="topic-cn">{article.topic_label_cn || '#新闻'}</span>
              </button>
            ))}
          </div>
        )}
      </section>

      {activeView === 'favorites' ? (
        <Favorites />
      ) : (
      <section className="learning-layout">
        <article className="learning-article">
          <div className="learning-article-header">
            <div className="header-top">
              <span className="source-badge">{selectedArticle.source}</span>
              <span className={`difficulty-badge ${getDifficultyClass(selectedArticle.difficulty_level)}`}>
                {selectedArticle.difficulty_level || 'CET6'}
              </span>
            </div>
            <h2>
              {renderAnnotatedParagraph(
                selectedArticle.title || '',
                selectedArticle.words || [],
                [],
                handleKnownWordClick,
                activeWordId,
                handleLookupWord,
                lookupPanel.state === 'loading' ? lookupPanel.word : '',
                { showGloss: false }
              )}
            </h2>
            <div className="meta">
              <span>{selectedArticle.published_at?.split('T')[0]}</span>
              {selectedArticle.url && (
                <a href={selectedArticle.url} target="_blank" rel="noopener noreferrer">View Original</a>
              )}
            </div>
          </div>

          <div className="learning-article-body">
            {(selectedArticle.content || '').split('\n').map((paragraph, index) => (
              <p key={index}>
                {renderAnnotatedParagraph(
                  paragraph,
                  selectedArticle.words || [],
                  selectedArticle.phrases || [],
                  handleKnownWordClick,
                  activeWordId,
                  handleLookupWord,
                  lookupPanel.state === 'loading' ? lookupPanel.word : ''
                )}
              </p>
            ))}
          </div>

          <CommentsSection key={selectedArticle.id} articleId={selectedArticle.id} />
        </article>

        <aside className="learning-vocab">
          <div className="vocab-tabs">
            <button
              className={`vocab-tab ${activeTab === 'words' ? 'active' : ''}`}
              onClick={() => setActiveTab('words')}
            >
              Words ({selectedArticle.words?.length || 0})
            </button>
            <button
              className={`vocab-tab ${activeTab === 'phrases' ? 'active' : ''}`}
              onClick={() => setActiveTab('phrases')}
            >
              Phrases ({selectedArticle.phrases?.length || 0})
            </button>
          </div>

          <div className="vocab-tab-content">
            {activeTab === 'words' && (
              <div className="words-list">
                {selectedArticle.words?.length ? selectedArticle.words.map(word => (
                  <div
                    key={word.id}
                    id={`word-card-${word.id}`}
                    className={`word-card ${activeWordId === word.id ? 'active' : ''}`}
                  >
                    <div className="word-header">
                      <div className="word-main">
                        <span className="word-text">{word.word}</span>
                        {word.pronunciation && <span className="word-pronunciation">{word.pronunciation}</span>}
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
                        onClick={() => handleHideWord(word.id, word.word)}
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
                      {word.part_of_speech && <span className="pos-badge">{word.part_of_speech}</span>}
                    </div>
                    {(word.definition || getDisplayDefinitionCn(word)) && (
                      <div className="word-definition-block">
                        <h4 className="section-title">Definition</h4>
                        {word.definition && <p className="word-definition">{word.definition}</p>}
                        {getContextMeaningCn(word) && (
                          <p className="word-definition-cn">
                            <span className="definition-label">当前语境义</span>
                            {getContextMeaningCn(word)}
                          </p>
                        )}
                        {getCommonMeaningCn(word) && (
                          <p className="word-definition-cn secondary">
                            <span className="definition-label">常见义</span>
                            {getCommonMeaningCn(word)}
                          </p>
                        )}
                        {!getContextMeaningCn(word) && !getCommonMeaningCn(word) && getDisplayDefinitionCn(word) && (
                          <p className="word-definition-cn">
                            {getDisplayDefinitionCn(word)}
                          </p>
                        )}
                      </div>
                    )}
                    {word.example_sentence && (
                      <div className="word-example">
                        <h4 className="section-title">Example</h4>
                        <p className="example-sentence">{word.example_sentence}</p>
                        {word.example_cn && <p className="example-cn">{word.example_cn}</p>}
                        {word.example_source && <span className="example-source">{word.example_source}</span>}
                      </div>
                    )}
                  </div>
                )) : <div className="no-content"><p>No vocabulary extracted yet.</p></div>}
              </div>
            )}

            {activeTab === 'phrases' && (
              <div className="phrases-list">
                {selectedArticle.phrases?.length ? selectedArticle.phrases.map(phrase => (
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
                        onClick={() => handleHidePhrase(phrase.id, phrase.phrase)}
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
                        <h4 className="section-title">Meaning</h4>
                        <p className="phrase-meaning">{phrase.meaning}</p>
                        {phrase.meaning_cn && <p className="phrase-meaning-cn">{phrase.meaning_cn}</p>}
                      </div>
                    )}
                    {phrase.example_sentence && (
                      <div className="phrase-example">
                        <h4 className="section-title">Example</h4>
                        <p className="example-sentence">{phrase.example_sentence}</p>
                        {phrase.example_cn && <p className="example-cn">{phrase.example_cn}</p>}
                        {phrase.example_source && <span className="example-source">{phrase.example_source}</span>}
                      </div>
                    )}
                  </div>
                )) : <div className="no-content"><p>No phrases extracted yet.</p></div>}
              </div>
            )}
          </div>
        </aside>
      </section>
      )}
      {lookupPanel.state !== 'idle' && (
        <div
          className={`lookup-popover ${lookupPanel.state} ${lookupPanel.placement}`}
          style={{ top: lookupPanel.top, left: lookupPanel.left }}
          onMouseDown={(event) => event.stopPropagation()}
        >
          {lookupPanel.data ? (
            <>
              <span className="lookup-popover-meaning">
                {getDisplayDefinitionCn(lookupPanel.data) || lookupPanel.data.definition || lookupPanel.data.word}
              </span>
              <button
                type="button"
                className={`lookup-popover-btn ${lookupPanel.data.in_word_list ? 'added' : ''}`}
                onClick={handleAddLookupToWords}
                title={lookupPanel.data.in_word_list ? 'Already in Words' : 'Add to Words'}
              >
                +
              </button>
              <button
                type="button"
                className={`lookup-popover-btn heart ${favoritedWords.has(lookupPanel.data.word) ? 'favorited' : ''}`}
                onClick={handleFavoriteLookupWord}
                title={favoritedWords.has(lookupPanel.data.word) ? 'Already favorited' : 'Add to favorites'}
              >
                {favoritedWords.has(lookupPanel.data.word) ? '♥' : '♡'}
              </button>
            </>
          ) : (
            <span className="lookup-popover-message">{lookupPanel.message}</span>
          )}
        </div>
      )}
    </div>
  )
}

export default App

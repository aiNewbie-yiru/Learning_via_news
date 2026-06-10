import re
from collections import Counter
from pathlib import Path
from typing import List, Dict, Tuple


def load_resource_word_list(filename: str) -> set:
    """Load one English word per line, or the first English token from tabbed lines."""
    path = Path(__file__).resolve().parent.parent / "resources" / filename
    if not path.exists():
        return set()

    words = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            match = re.match(r"\s*([A-Za-z]+(?:'[A-Za-z]+)?)\b", line)
            if match:
                words.add(match.group(1).lower())
    return words


def get_basic_candidate_forms(word: str) -> set:
    """Return conservative base-form candidates for common English inflections."""
    candidates = set()
    word = word.lower().strip()
    if len(word) <= 3:
        return candidates

    if word.endswith("ies") and len(word) > 4:
        candidates.add(word[:-3] + "y")
    if word.endswith("es") and len(word) > 4:
        candidates.add(word[:-2])
    if word.endswith("s") and len(word) > 3:
        candidates.add(word[:-1])
    if word.endswith("ied") and len(word) > 4:
        candidates.add(word[:-3] + "y")
    if word.endswith("ed") and len(word) > 4:
        candidates.add(word[:-2])
        candidates.add(word[:-1])
        if len(word) > 5 and word[-3] == word[-4]:
            candidates.add(word[:-3])
    if word.endswith("ing") and len(word) > 5:
        candidates.add(word[:-3])
        candidates.add(word[:-3] + "e")
        if len(word) > 6 and word[-4] == word[-5]:
            candidates.add(word[:-4])
    if word.endswith("ly") and len(word) > 5:
        candidates.add(word[:-2])
    if word.endswith("er") and len(word) > 4:
        candidates.add(word[:-2])
    if word.endswith("est") and len(word) > 5:
        candidates.add(word[:-3])

    return {candidate for candidate in candidates if len(candidate) >= 3}

# 基础词汇 - 初中及以下水平（包含最常见的3000词）
BASIC_WORDS = set([
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
    'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
    'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
    'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what',
    'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go', 'me',
    'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know', 'take',
    'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
    'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also',
    'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way',
    'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
    'is', 'are', 'was', 'were', 'been', 'has', 'had', 'may', 'might', 'must',
    'should', 'would', 'could', 'need', 'dare', 'ought', 'used', 'going', 'gone',
    'get', 'got', 'gotten', 'go', 'went', 'come', 'came', 'run', 'ran', 'see', 'saw',
    'seen', 'say', 'said', 'do', 'did', 'done', 'make', 'made', 'take', 'took', 'taken',
    'give', 'gave', 'given', 'find', 'found', 'tell', 'told', 'ask', 'asked', 'answer',
    'answered', 'address', 'age', 'air', 'animal', 'apple', 'arm', 'art', 'baby', 'back',
    'ball', 'banana', 'bank', 'bed', 'bell', 'bird', 'birthday', 'black', 'blue', 'book',
    'boy', 'bread', 'brother', 'building', 'bus', 'butter', 'cake', 'car', 'card', 'cat',
    'chair', 'child', 'children', 'city', 'class', 'clock', 'coat', 'coffee', 'cold',
    'color', 'country', 'day', 'dog', 'door', 'earth', 'eat', 'egg', 'end', 'eye',
    'face', 'family', 'father', 'fish', 'floor', 'food', 'foot', 'garden', 'girl',
    'glass', 'good', 'grass', 'green', 'hand', 'head', 'heart', 'help', 'home', 'house',
    'ice', 'idea', 'job', 'jump', 'key', 'kind', 'land', 'life', 'light', 'like',
    'line', 'list', 'look', 'love', 'man', 'men', 'money', 'morning', 'mother', 'name',
    'night', 'nose', 'oil', 'old', 'paper', 'party', 'people', 'picture', 'place',
    'plant', 'play', 'rain', 'river', 'road', 'room', 'school', 'sea', 'season',
    'ship', 'shoe', 'side', 'sky', 'sleep', 'smile', 'snow', 'song', 'sound', 'star',
    'start', 'step', 'story', 'sun', 'table', 'talk', 'teacher', 'telephone', 'television',
    'thing', 'time', 'top', 'tree', 'water', 'way', 'weather', 'week', 'white', 'woman',
    'women', 'world', 'year', 'yes', 'no', 'please', 'thank', 'thanks', 'hello', 'goodbye',
    'sorry', 'okay', 'today', 'tomorrow', 'yesterday', 'here', 'there', 'everywhere',
    'somewhere', 'nowhere', 'where', 'when', 'why', 'how', 'what', 'which', 'who',
    'whom', 'whose', 'this', 'that', 'these', 'those', 'all', 'both', 'each', 'few',
    'many', 'more', 'most', 'much', 'no', 'none', 'one', 'only', 'other', 'several',
    'some', 'such', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'even', 'also',
    'still', 'yet', 'already', 'always', 'never', 'often', 'sometimes', 'usually',
    'hardly', 'scarcely', 'barely', 'almost', 'nearly', 'above', 'across', 'after',
    'against', 'along', 'among', 'around', 'at', 'before', 'behind', 'below', 'beneath',
    'beside', 'between', 'beyond', 'by', 'down', 'during', 'except', 'for', 'from',
    'in', 'inside', 'into', 'like', 'near', 'of', 'off', 'on', 'onto', 'out',
    'outside', 'over', 'past', 'since', 'through', 'throughout', 'till', 'to',
    'toward', 'under', 'until', 'up', 'upon', 'with', 'within', 'without'
])

# Temporary machine-readable proxy for the compulsory-education vocabulary floor.
# Product rule: replace this with a hand-cleaned machine-readable list from the
# official 2022 curriculum when available. Do not use NGSL or high-school lists.
BASIC_WORDS.update(load_resource_word_list("compulsory_basic_words_junior_proxy.txt"))

# 四级词汇 (CET4) - 在Basic基础上扩展
# 确保 Basic ⊂ CET4，移除与Basic重叠的词后共1423个专有词
CET4_WORDS = BASIC_WORDS.union(set([
    'abandon', 'ability', 'able', 'absence', 'absolute', 'absorb', 'abstract', 'academic', 'accept', 'access',
    'accident', 'accompany', 'accomplish', 'according', 'account', 'accurate', 'achieve', 'acquire', 'action', 'active',
    'activity', 'actual', 'adapt', 'addition', 'adequate', 'adjust', 'administration', 'admit', 'adopt', 'advance',
    'advantage', 'adventure', 'advice', 'advise', 'affect', 'afford', 'agency', 'agent', 'aggressive', 'agree',
    'agreement', 'ahead', 'aim', 'aircraft', 'alcohol', 'alike', 'alive', 'allow', 'alone', 'alter',
    'alternative', 'although', 'amaze', 'ambition', 'amount', 'analysis', 'analyze', 'ancient', 'angle', 'angry',
    'announce', 'annual', 'another', 'anxiety', 'anxious', 'apart', 'apparent', 'appeal', 'appear', 'appreciate',
    'approach', 'appropriate', 'approval', 'approve', 'argue', 'argument', 'arise', 'arrange', 'arrest', 'arrive',
    'article', 'artistic', 'aspect', 'assess', 'assign', 'assignment', 'assist', 'assistance', 'assistant', 'associate',
    'assume', 'assure', 'athlete', 'atmosphere', 'attach', 'attack', 'attain', 'attempt', 'attend', 'attention',
    'attitude', 'attract', 'audience', 'author', 'authority', 'available', 'average', 'avoid', 'award', 'aware',
    'background', 'balance', 'barrier', 'base', 'basic', 'basis', 'battle', 'beauty', 'become', 'behavior',
    'belief', 'believe', 'belong', 'benefit', 'besides', 'best', 'better', 'billion', 'biology', 'birth',
    'bit', 'bitter', 'blame', 'blank', 'blind', 'blood', 'blow', 'board', 'boat', 'body',
    'bold', 'border', 'born', 'borrow', 'boss', 'bottle', 'bottom', 'bound', 'bow', 'brain',
    'branch', 'brand', 'brave', 'break', 'breakfast', 'breath', 'breathe', 'brick', 'bridge', 'brief',
    'bright', 'bring', 'broad', 'broadcast', 'budget', 'build', 'burn', 'burst', 'business', 'busy',
    'button', 'buy', 'cabin', 'cable', 'calculate', 'calendar', 'call', 'calm', 'camera', 'camp',
    'campaign', 'campus', 'cancel', 'cancer', 'candidate', 'capital', 'captain', 'capture', 'care', 'career',
    'careful', 'carefully', 'carry', 'case', 'cash', 'cast', 'catch', 'category', 'cause', 'cease',
    'celebrate', 'center', 'central', 'century', 'certain', 'chain', 'challenge', 'champion', 'chance', 'change',
    'character', 'characteristic', 'charge', 'charity', 'chart', 'check', 'cheer', 'chemical', 'chemistry', 'choice',
    'choose', 'church', 'circle', 'circuit', 'civil', 'claim', 'classic', 'classify', 'clean', 'clear',
    'clearly', 'client', 'climate', 'climb', 'close', 'closely', 'cloth', 'clothes', 'cloud', 'club',
    'coach', 'coal', 'coast', 'collar', 'collect', 'collection', 'college', 'combine', 'comfort', 'comfortable',
    'command', 'comment', 'commercial', 'commission', 'commit', 'committee', 'common', 'communicate', 'communication', 'community',
    'company', 'compare', 'comparison', 'compete', 'competition', 'complain', 'complete', 'completely', 'complex', 'complicated',
    'component', 'compose', 'comprise', 'computer', 'concentrate', 'concept', 'concern', 'concerned', 'conclude', 'conclusion',
    'concrete', 'condition', 'conduct', 'conference', 'confident', 'confirm', 'conflict', 'confuse', 'confusion', 'congress',
    'connect', 'connection', 'conscious', 'consent', 'consequence', 'consider', 'considerable', 'consideration', 'consist', 'consistent',
    'constant', 'construct', 'construction', 'consult', 'consume', 'contact', 'contain', 'content', 'contract', 'contrast',
    'contribute', 'control', 'convention', 'conversation', 'convert', 'convey', 'convince', 'cook', 'cool', 'cooperate',
    'copy', 'core', 'corn', 'corner', 'corporate', 'correct', 'correspond', 'cost', 'cottage', 'cotton',
    'cough', 'count', 'counter', 'county', 'couple', 'courage', 'course', 'court', 'cover', 'craft',
    'crash', 'create', 'creation', 'creative', 'credit', 'crew', 'crime', 'criminal', 'crisis', 'critic',
    'critical', 'criticism', 'criticize', 'crop', 'cross', 'crowd', 'cruel', 'cry', 'cultural', 'culture',
    'cup', 'current', 'curriculum', 'custom', 'customer', 'cut', 'damage', 'dance', 'danger', 'dark',
    'data', 'date', 'daughter', 'dead', 'deal', 'dear', 'death', 'debate', 'debt', 'decade',
    'decide', 'decision', 'declare', 'decline', 'decorate', 'decrease', 'deep', 'deeply', 'deer', 'defeat',
    'defend', 'defense', 'deficit', 'define', 'definite', 'definition', 'degree', 'delay', 'deliver', 'demand',
    'democracy', 'demonstrate', 'deny', 'department', 'depend', 'dependent', 'describe', 'description', 'desert', 'design',
    'desire', 'destroy', 'detail', 'detect', 'determine', 'develop', 'development', 'device', 'devote', 'diagram',
    'dialogue', 'diamond', 'die', 'diet', 'differ', 'difference', 'different', 'difficult', 'difficulty', 'digital',
    'dignity', 'dinner', 'direct', 'direction', 'directly', 'director', 'dirt', 'dirty', 'disappear', 'disappoint',
    'disaster', 'discover', 'discussion', 'disease', 'dismiss', 'display', 'distance', 'distant', 'distinct', 'distinguish',
    'distribute', 'divide', 'division', 'doctor', 'document', 'dollar', 'domestic', 'dominant', 'double', 'doubt',
    'dozen', 'draft', 'draw', 'dream', 'dress', 'drink', 'drive', 'driver', 'drop', 'drug',
    'dry', 'due', 'dust', 'duty', 'early', 'earn', 'ease', 'east', 'easy', 'economic',
    'economy', 'edge', 'education', 'effect', 'effective', 'efficiency', 'efficient', 'effort', 'either', 'elaborate',
    'elastic', 'electric', 'electricity', 'electronic', 'element', 'elementary', 'elephant', 'elevator', 'eliminate', 'else',
    'elsewhere', 'email', 'empty', 'enable', 'encourage', 'enemy', 'energy', 'enforce', 'engage', 'engine',
    'engineer', 'engineering', 'enjoy', 'enormous', 'enough', 'enter', 'enterprise', 'entertain', 'enthusiasm', 'entire',
    'entirely', 'entry', 'environment', 'environmental', 'equal', 'equality', 'equipment', 'error', 'escape', 'especially',
    'essay', 'essential', 'establish', 'establishment', 'estimate', 'evaluate', 'evening', 'event', 'eventually', 'ever',
    'every', 'evidence', 'evident', 'evil', 'example', 'excellent', 'exception', 'exchange', 'excite', 'excitement',
    'exclude', 'excuse', 'execute', 'executive', 'exercise', 'exhibit', 'expand', 'expect', 'expense', 'expensive',
    'experience', 'experiment', 'expert', 'explain', 'explanation', 'explore', 'export', 'express', 'expression', 'extend',
    'extent', 'external', 'extra', 'extreme', 'fact', 'factory', 'fair', 'fairly', 'faith', 'fall',
    'false', 'famous', 'fan', 'fashion', 'fast', 'fasten', 'fat', 'fear', 'feature', 'federal',
    'feed', 'feel', 'feeling', 'female', 'fence', 'few', 'field', 'fierce', 'fight', 'figure', 'fill',
    'film', 'final', 'finally', 'finance', 'financial', 'find', 'fine', 'finger', 'finish', 'fire', 'firm',
    'fish', 'fit', 'five', 'fix', 'flight', 'float', 'flood', 'flow', 'flower', 'fly', 'focus',
    'follow', 'fool', 'foot', 'football', 'forbid', 'force', 'forecast', 'foreign', 'forest', 'forever', 'forget',
    'forgive', 'form', 'formal', 'format', 'former', 'fortunate', 'fortunately', 'fortune', 'forward', 'foundation',
    'four', 'free', 'freedom', 'fresh', 'friend', 'friendly', 'friendship', 'frighten', 'front', 'fruit',
    'full', 'fully', 'fun', 'function', 'fund', 'fundamental', 'funny', 'future', 'gain', 'game',
    'gas', 'gather', 'general', 'generally', 'generate', 'generation', 'generous', 'genius', 'gentle', 'gently',
    'gift', 'glad', 'global', 'goal', 'government', 'grade', 'graduate', 'grain', 'grand', 'grant',
    'great', 'ground', 'group', 'grow', 'growth', 'guard', 'guess', 'guest', 'guide', 'guilt',
    'guilty', 'hair', 'half', 'hang', 'happen', 'happy', 'hard', 'harm', 'hate', 'health',
    'healthy', 'hear', 'heat', 'heavy', 'height', 'hero', 'high', 'highly', 'hill', 'history',
    'hit', 'hold', 'hole', 'home', 'honest', 'honestly', 'honor', 'hope', 'horizon', 'hospital', 'host',
    'hot', 'hotel', 'hour', 'however', 'huge', 'human', 'humor', 'hundred', 'hungry', 'hunt',
    'hurry', 'hurt', 'husband', 'identify', 'ignore', 'ill', 'illegal', 'illness', 'image', 'imagine',
    'immediate', 'immediately', 'import', 'importance', 'important', 'impossible', 'impress', 'impression', 'improve', 'include',
    'including', 'income', 'increase', 'incredible', 'independent', 'index', 'indicate', 'individual', 'indoor', 'industrial',
    'industry', 'influence', 'inform', 'information', 'initial', 'initially', 'inject', 'injury', 'insist', 'install',
    'instance', 'instant', 'instead', 'institute', 'institution', 'instruct', 'instruction', 'instrument', 'insurance', 'intellectual',
    'intelligence', 'intelligent', 'intend', 'intense', 'intention', 'interest', 'interested', 'interesting', 'international', 'internet',
    'interpret', 'interval', 'interview', 'introduce', 'invent', 'investment', 'involve', 'iron', 'island', 'issue',
    'join', 'joint', 'journey', 'judge', 'judgment', 'keep', 'kill', 'kitchen', 'knee', 'knife',
    'knowledge', 'labor', 'lack', 'ladder', 'lady', 'lake', 'language', 'large', 'largely', 'last',
    'late', 'later', 'laugh', 'law', 'lead', 'leader', 'leadership', 'learn', 'least', 'leave',
    'lecture', 'left', 'leg', 'legal', 'length', 'lesson', 'let', 'letter', 'level', 'liberal',
    'library', 'license', 'lie', 'life', 'lift', 'likely', 'limit', 'limitation', 'limited', 'link', 'listen',
    'literature', 'little', 'live', 'living', 'load', 'local', 'locate', 'location', 'lock', 'long',
    'look', 'lose', 'loss', 'lot', 'love', 'low', 'machine', 'magazine', 'main', 'mainly', 'maintain', 'major',
    'majority', 'make', 'male', 'man', 'manage', 'management', 'manager', 'manner', 'manufacture', 'map', 'market', 'marriage',
    'married', 'mass', 'master', 'material', 'matter', 'maybe', 'mean', 'meaning', 'means', 'measure',
    'meat', 'media', 'medical', 'medicine', 'meet', 'meeting', 'member', 'memory', 'mental', 'mention',
    'message', 'method', 'middle', 'military', 'milk', 'million', 'mind', 'mine', 'minimum', 'minute',
    'miss', 'mission', 'mistake', 'mix', 'model', 'modern', 'moment', 'monitor', 'month', 'mood',
    'moon', 'more', 'morning', 'mother', 'motion', 'motor', 'mountain', 'mouth', 'move', 'movement', 'movie', 'myself',
    'nation', 'national', 'nature', 'necessary', 'negative', 'neighbor', 'neighborhood', 'neither', 'nervous', 'network', 'nevertheless',
    'news', 'newspaper', 'next', 'nice', 'nine', 'normal', 'north', 'northern', 'note', 'notebook',
    'nothing', 'notice', 'nowadays', 'number', 'nurse', 'object', 'obvious', 'occasion', 'occasional', 'occupation',
    'occur', 'ocean', 'offer', 'office', 'officer', 'official', 'often', 'oil', 'old', 'once', 'open', 'operation', 'opinion',
    'opportunity', 'opposite', 'option', 'order', 'ordinary', 'organize', 'origin', 'original', 'otherwise', 'outcome',
    'overall', 'owner', 'page', 'pain', 'paint', 'parent', 'park', 'part', 'particular', 'particularly',
    'partner', 'pass', 'passage', 'passenger', 'past', 'pay', 'peace', 'peaceful', 'peak', 'pen', 'percent',
    'perfect', 'perform', 'performance', 'perhaps', 'period', 'permanent', 'permission', 'person', 'personal', 'personality',
    'perspective', 'persuade', 'phase', 'phone', 'photo', 'phrase', 'physical', 'pick', 'piece', 'pilot',
    'plain', 'plan', 'plastic', 'plate', 'play', 'please', 'plenty', 'point', 'police', 'policy', 'politics', 'pollute',
    'pollution', 'poor', 'popular', 'population', 'port', 'position', 'positive', 'possible', 'possibly', 'post',
    'potential', 'power', 'powerful', 'practice', 'prepare', 'present', 'presentation', 'preserve', 'press', 'pressure',
    'prevent', 'price', 'pride', 'primary', 'principle', 'print', 'private', 'probable', 'problem', 'process',
    'produce', 'product', 'production', 'profit', 'program', 'progress', 'project', 'promise', 'promote', 'proper',
    'property', 'protect', 'protection', 'prove', 'provide', 'public', 'publication', 'publish', 'pull', 'pulse',
    'pump', 'purchase', 'pure', 'purpose', 'push', 'put', 'quality', 'quantity', 'question', 'quick',
    'quickly', 'quiet', 'quit', 'quite', 'race', 'radio', 'raise', 'range', 'rate', 'rather',
    'raw', 'reach', 'read', 'ready', 'real', 'reality', 'realize', 'really', 'reason', 'reasonable',
    'receive', 'recent', 'recently', 'recognize', 'record', 'recover', 'reduce', 'refer', 'reference', 'reflect',
    'reform', 'refuse', 'region', 'register', 'regular', 'regulation', 'reinforce', 'reject', 'relate', 'relation',
    'relationship', 'relative', 'relax', 'release', 'relevant', 'relief', 'religion', 'religious', 'rely', 'remain',
    'remark', 'remember', 'remind', 'remove', 'replace', 'reply', 'report', 'represent', 'representative', 'republic',
    'request', 'require', 'research', 'resemble', 'reserve', 'resident', 'resign', 'resist', 'resolve', 'resource',
    'respect', 'responsible', 'rest', 'result', 'return', 'reveal', 'review', 'revolution', 'reward', 'rich',
    'ride', 'right', 'ring', 'rise', 'risk', 'rock', 'role', 'roll', 'root', 'rule',
    'safe', 'safety', 'sale', 'salt', 'sample', 'satellite', 'satisfy', 'save', 'scene', 'schedule',
    'science', 'scientific', 'scientist', 'score', 'screen', 'search', 'season', 'seat', 'second', 'secret', 'section',
    'security', 'seek', 'seem', 'sell', 'send', 'senior', 'sense', 'sensitive', 'separate', 'series',
    'serious', 'serve', 'service', 'set', 'settle', 'seven', 'severe', 'sex', 'share', 'sharp',
    'shelf', 'shell', 'shift', 'shine', 'ship', 'shirt', 'shock', 'short', 'shoulder', 'show', 'side',
    'sign', 'signal', 'silent', 'simple', 'simply', 'since', 'sing', 'single', 'sink', 'site', 'situation', 'size', 'skill',
    'skin', 'sleep', 'slow', 'slowly', 'small', 'smile', 'smoke', 'smooth', 'social', 'society', 'soft',
    'software', 'soil', 'solar', 'soldier', 'solution', 'solve', 'something', 'son', 'soon', 'source',
    'south', 'space', 'speak', 'special', 'specific', 'speed', 'spell', 'spend', 'split', 'spoil',
    'spread', 'spring', 'stand', 'standard', 'star', 'start', 'state', 'statement', 'station', 'stay', 'stick', 'stock',
    'stop', 'store', 'storm', 'story', 'straight', 'strange', 'street', 'strength', 'strong', 'structure', 'student',
    'study', 'stuff', 'style', 'subject', 'submit', 'succeed', 'success', 'successful', 'sudden', 'suddenly',
    'suffer', 'sufficient', 'suggest', 'suggestion', 'suit', 'summer', 'sun', 'supply', 'support', 'suppose', 'sure',
    'surface', 'system', 'table', 'take', 'talk', 'task', 'tax', 'tea', 'teach', 'team',
    'technology', 'temperature', 'temporary', 'ten', 'tend', 'term', 'terrible', 'test', 'than', 'that',
    'the', 'their', 'them', 'then', 'theory', 'there', 'therefore', 'these', 'they', 'thing', 'think', 'third', 'this', 'those', 'though', 'thought',
    'thousand', 'three', 'throw', 'thus', 'tiny', 'tip', 'tire', 'title', 'together', 'tone',
    'topic', 'touch', 'tower', 'town', 'trace', 'trade', 'traditional', 'traffic', 'train', 'training',
    'transfer', 'transform', 'transport', 'travel', 'treat', 'treatment', 'tree', 'trial', 'trip', 'trouble', 'true',
    'trust', 'truth', 'try', 'turn', 'twenty', 'type', 'understand', 'union', 'unit', 'university',
    'unless', 'useful', 'user', 'usual', 'value', 'various', 'very', 'victim', 'view', 'village', 'visit',
    'voice', 'volume', 'vote', 'wait', 'walk', 'wall', 'war', 'warm', 'warn', 'wash',
    'waste', 'watch', 'weak', 'wealth', 'wear', 'weather', 'week', 'weigh', 'weight', 'welcome',
    'well', 'west', 'whatever', 'when', 'where', 'whether', 'which', 'while', 'white', 'who', 'whole', 'whom', 'whose', 'why', 'wide', 'widely',
    'wife', 'wild', 'win', 'wind', 'window', 'wine', 'winter', 'with', 'within', 'without', 'woman', 'wood', 'word', 'worker', 'world',
    'worry', 'write', 'writer', 'wrong', 'young', 'yourself', 'youth', 'zero'
]))

# 六级词汇 (CET6) - 在四级基础上扩展
CET6_WORDS = CET4_WORDS.union(set([
    'abnormal', 'absurd', 'abundant', 'accessory', 'accommodate', 'acquisition',
    'acquaintance', 'activate', 'acute', 'adhere', 'adjacent', 'adjoin',
    'administer', 'admission', 'adolescent', 'adverse', 'advertise', 'advocate',
    'aerial', 'affirm', 'afflict', 'aggregate', 'ailment', 'allege', 'alternate',
    'ambiguous', 'ambitious', 'amend', 'amorphous', 'analogy', 'anonymous',
    'antagonize', 'antenna', 'apparatus', 'applaud', 'applicable', 'appoint',
    'appraisal', 'apprehend', 'aptitude', 'arbitrary', 'arbitrate', 'ardent',
    'arena', 'articulate', 'ascend', 'ascertain', 'ascribe', 'assault',
    'assemble', 'assent', 'assert', 'assort', 'astonish', 'astound',
    'atmospheric', 'attain', 'attribute', 'auction', 'authentic', 'authorize',
    'autonomous', 'avail', 'avert', 'avow', 'badge', 'balcony', 'ban',
    'barren', 'batch', 'bearer', 'befall', 'belch', 'bend', 'beneath',
    'besiege', 'bestow', 'betray', 'bias', 'bilingual', 'bizarre', 'blast',
    'blaze', 'bleed', 'blend', 'bless', 'blossom', 'blunder', 'blunt', 'blur',
    'boast', 'boil', 'bolt', 'bond', 'boom', 'boost', 'boundary', 'boycott',
    'brace', 'bracket', 'breakthrough', 'breed', 'briefcase', 'brilliant',
    'brisk', 'bronze', 'browse', 'bruise', 'brutal', 'bubble', 'bud', 'buffer',
    'bulk', 'bump', 'bunch', 'bundle', 'bureau', 'burden', 'bureaucracy',
    'bypass', 'cafeteria', 'calcium', 'calorie', 'capable', 'capacity',
    'caption', 'carve', 'casualty', 'catastrophe', 'cater', 'census',
    'ceremony', 'chaos', 'chapter', 'characterize', 'charm', 'charter',
    'chase', 'chill', 'chip', 'chord', 'chronic', 'chunk', 'circumstance',
    'cite', 'civilian', 'clamp', 'clarity', 'clash', 'clasp', 'classification',
    'clause', 'claw', 'clay', 'cleavage', 'clerk', 'climax', 'cling', 'clip',
    'cloak', 'clue', 'cluster', 'clutch', 'coerce', 'cognitive', 'coherent',
    'coincide', 'collaborate', 'collapse', 'colleague', 'collective',
    'colonial', 'colony', 'comb', 'combat', 'comic', 'commemorate',
    'commence', 'commend', 'commitment', 'commodity', 'commonplace',
    'compatible', 'compel', 'compensate', 'compile', 'complaint',
    'complement', 'complexity', 'complicate', 'compliment', 'comply',
    'comprehend', 'comprehensive', 'compress', 'compromise', 'conceal',
    'concede', 'conceive', 'conception', 'concise', 'concur', 'condemn',
    'condense', 'confer', 'confess', 'confidence', 'confidential',
    'configuration', 'confine', 'conform', 'confront', 'conjunction',
    'connotation', 'conquer', 'conscience', 'conscientious', 'consecutive',
    'conservation', 'conservative', 'consolidate', 'conspicuous',
    'constituent', 'constitute', 'constrain', 'consultant', 'contaminate',
    'contemplate', 'contemporary', 'contend', 'contest', 'context',
    'contradict', 'contrary', 'controversy', 'convene', 'converge',
    'conviction', 'coordinate', 'cope', 'correlate', 'corrode', 'corrupt',
    'cosmic', 'costume', 'council', 'counsel', 'counterpart', 'courtesy',
    'coverage', 'coward', 'crack', 'crave', 'credible', 'criteria',
    'crucial', 'crude', 'cruise', 'crush', 'crystal', 'cube', 'cubic',
    'cultivate', 'cumulative', 'curb', 'custody', 'dagger', 'damn', 'damp',
    'dangerous', 'dash', 'database', 'dazzle', 'deadly', 'dealer', 'debris',
    'deceit', 'deceive', 'decimal', 'declaration', 'dedicate', 'deduce',
    'deem', 'default', 'defect', 'deficient', 'deform', 'delegate',
    'deliberate', 'delicate', 'delusion', 'demanding', 'denial', 'dense',
    'density', 'depict', 'deposit', 'depress', 'depression', 'deprive',
    'derive', 'descend', 'deserve', 'designate', 'desperate', 'despise',
    'destiny', 'destruction', 'detach', 'detain', 'deteriorate', 'deviate',
    'devise', 'devour', 'diagnose', 'dictate', 'differentiate', 'diffuse',
    'digest', 'dilute', 'diminish', 'dine', 'dioxide', 'diploma', 'diplomat',
    'diplomatic', 'discard', 'discern', 'discharge', 'discipline',
    'disclaim', 'disclose', 'discount', 'discourage', 'discriminate',
    'disguise', 'disgust', 'dismay', 'dispatch', 'disperse', 'displace',
    'dispose', 'dispute', 'disseminate', 'dissipate', 'distinction',
    'distort', 'distract', 'diverse', 'diversion', 'dividend', 'divine',
    'dominate', 'donate', 'dormant', 'doubtful', 'drama', 'dramatic',
    'drastic', 'drawback', 'dribble', 'drift', 'drill', 'drip', 'drown',
    'dubious', 'duly', 'duplicate', 'duration', 'dusk', 'dwell', 'dynamic',
    'dynamo', 'earnest', 'eclipse', 'ecology', 'ecosystem', 'edible', 'edit',
    'edition', 'editor', 'educator', 'elapse', 'elect', 'election',
    'electron', 'elegant', 'eliminate', 'elite', 'eloquent', 'embarrass',
    'embed', 'embody', 'embrace', 'emerge', 'emission', 'emit', 'empirical',
    'empower', 'enact', 'encircle', 'enclose', 'encompass', 'encounter',
    'endanger', 'endorse', 'endow', 'endure', 'engrave', 'enhance',
    'enlighten', 'enroll', 'ensure', 'entail', 'entity', 'entitle',
    'entrance', 'envelope', 'episode', 'equate', 'equilibrium', 'equivalent',
    'era', 'erosion', 'err', 'erroneous', 'escalate', 'escort', 'essence',
    'estate', 'esteem', 'eternal', 'ethnic', 'evacuate', 'evaporate',
    'eventual', 'evoke', 'exceptional', 'excerpt', 'exclusive', 'exert',
    'exile', 'expansion', 'expectation', 'expedition', 'expel', 'expend',
    'expertise', 'explicit', 'exploit', 'exploration', 'explosive', 'expose',
    'exposition', 'extensive', 'extinct', 'extinguish', 'extract',
    'extraordinary', 'fable', 'facility', 'fade', 'faint', 'fake', 'fallacy',
    'famine', 'fantastic', 'fascinate', 'feasible', 'feast', 'feat',
    'feeble', 'fellow', 'ferry', 'fertile', 'fertilizer', 'fetus', 'fiber',
    'fiction', 'file', 'filter', 'fiscal', 'flame', 'flap', 'flare', 'flash',
    'flatter', 'flaw', 'flee', 'fling', 'fluctuate', 'fluffy', 'fluid',
    'flush', 'foam', 'forerunner', 'foresee', 'forge', 'formidable',
    'formula', 'fracture', 'fragile', 'fragrant', 'franchise', 'frantic',
    'fraud', 'friction', 'frost', 'frown', 'frustrate', 'furious',
    'furnish', 'fuse', 'fuss', 'galaxy', 'gamble', 'gap', 'garment', 'gasp',
    'gear', 'gender', 'gene', 'generalize', 'genetic', 'genuine', 'gesture',
    'ghost', 'gigantic', 'glamour', 'glance', 'glare', 'glide', 'glimpse',
    'glitter', 'globe', 'gloom', 'glorious', 'glow', 'govern', 'governor',
    'grab', 'grace', 'gracious', 'graphic', 'grasp', 'grateful', 'grave',
    'gravity', 'grease', 'grief', 'grind', 'grip', 'groan', 'groom', 'grope',
    'gross', 'guarantee', 'guideline', 'guitar', 'gulf', 'gum', 'hail',
    'halt', 'hammer', 'handbook', 'handicap', 'harbor', 'hardship',
    'harmony', 'harness', 'harsh', 'haste', 'hasty', 'hazard', 'headline',
    'headquarters', 'heal', 'heap', 'hearing', 'hearty', 'heave', 'hedge',
    'heel', 'heighten', 'heir', 'hemisphere', 'hence', 'herald', 'herb',
    'herd', 'hesitate', 'hide', 'hierarchy', 'highlight', 'hinder', 'hinge',
    'hint', 'hip', 'hire', 'hobby', 'hoist', 'holy', 'homogeneous', 'honey',
    'horizontal', 'horn', 'horror', 'hostile', 'hover', 'howl', 'huddle',
    'hug', 'humble', 'humid', 'humiliate', 'hypothesis', 'hysterical',
    'iceberg', 'ideal', 'identical', 'idle', 'ignite', 'ignorant',
    'illuminate', 'illusion', 'illustrate', 'imitate', 'immature', 'immense',
    'immigrant', 'immune', 'impact', 'impair', 'impart', 'impartial',
    'impatient', 'imperative', 'imperial', 'impetus', 'implement',
    'implicate', 'implication', 'implicit', 'imply', 'impose', 'improper',
    'impulse', 'inaccessible', 'inadequate', 'incapable', 'incidence',
    'incident', 'incline', 'inclusive', 'incorporate', 'incredible', 'incur',
    'indefinite', 'independence', 'indifference', 'indignant',
    'indispensable', 'induce', 'inevitable', 'infect', 'infer', 'inferior',
    'infinite', 'inflation', 'influential', 'inherent', 'inherit', 'initiate',
    'injustice', 'innocent', 'innovation', 'input', 'inquire', 'inquiry',
    'insect', 'insert', 'insight', 'inspect', 'inspire', 'instinct',
    'insulate', 'integrate', 'integrity', 'intensive', 'interact',
    'intercourse', 'interface', 'interfere', 'interim', 'interior',
    'internal', 'interrupt', 'intervention', 'intimidate', 'intricate',
    'intrigue', 'intrinsic', 'invalid', 'invaluable', 'invariably',
    'invasion', 'inverse', 'investigate', 'investor', 'invitation', 'invoke',
    'irony', 'irrespective', 'irritate', 'isolate', 'ivory', 'jade',
    'jargon', 'jealous', 'jewel', 'jolly', 'journal', 'journalist',
    'judicial', 'junction', 'jury', 'justify', 'keen', 'kernel', 'kettle',
    'keyboard', 'kidnap', 'kin', 'kit', 'knot', 'label', 'laboratory', 'lag',
    'lamb', 'lame', 'landmark', 'landscape', 'lane', 'lap', 'laptop', 'lash',
    'latitude', 'launch', 'laundry', 'lawful', 'layman', 'layout', 'leak',
    'lean', 'leap', 'lease', 'legacy', 'legitimate', 'lemon', 'lens',
    'lessen', 'lethal', 'liable', 'liberty', 'likelihood', 'limb', 'linear',
    'linguistic', 'lion', 'literally', 'literary', 'litter', 'loan',
    'lobby', 'locomotive', 'lodge', 'lofty', 'logic', 'logical', 'longing',
    'loop', 'loose', 'loosen', 'lord', 'lounge', 'lowland', 'loyal',
    'loyalty', 'lucid', 'lump', 'lunar', 'luxury', 'machinery', 'magic',
    'magnetic', 'magnificent', 'magnitude', 'mail', 'majesty', 'mammal',
    'mandate', 'manifest', 'manipulate', 'mankind', 'manor', 'manual',
    'margin', 'marine', 'marvel', 'masculine', 'massive', 'mature',
    'maximum', 'mechanism', 'mediate', 'melody', 'membership', 'memorial',
    'memorize', 'merchant', 'mercury', 'merge', 'merit', 'mess', 'metallic',
    'metaphor', 'methodology', 'microscope', 'midst', 'migrate', 'mild',
    'mill', 'minimize', 'minor', 'minority', 'miracle', 'miserable',
    'mislead', 'moan', 'mobile', 'moderate', 'modify', 'moist', 'molecule',
    'momentum', 'monarch', 'monopoly', 'monotony', 'monument', 'moral',
    'mortgage', 'mosaic', 'motive', 'mount', 'mourn', 'multiply',
    'municipal', 'murder', 'muscle', 'mushroom', 'mutual', 'mysterious',
    'myth', 'naive', 'naked', 'narrative', 'narrow', 'nationwide', 'native',
    'natural', 'negotiate', 'nerve', 'neutral', 'nickel', 'nightmare',
    'nominal', 'nominate', 'nonetheless', 'nonprofit', 'notable', 'notorious',
    'novel', 'nuclear', 'nucleus', 'numerical', 'numerous', 'nutrition',
    'oak', 'obedient', 'objection', 'objective', 'obligation', 'obscure',
    'observation', 'obsession', 'obsolete', 'odd', 'offend', 'offensive',
    'offset', 'omit', 'opaque', 'optimistic', 'orient', 'orientation',
    'originate', 'ornament', 'orthodox', 'outbreak', 'outfit', 'outlook',
    'outstanding', 'overcome', 'overflow', 'overhaul', 'overlap', 'overseas',
    'overtake', 'overthrow', 'overwhelm', 'oxide', 'oxygen', 'pact', 'panel',
    'panic', 'parade', 'paradigm', 'paragraph', 'parallel', 'parameter',
    'parasite', 'parliament', 'partial', 'participate', 'particle',
    'passion', 'passive', 'paste', 'patent', 'pathetic', 'patience',
    'patriotic', 'patrol', 'pattern', 'pause', 'pedestrian', 'penalty',
    'pension', 'perceive', 'percentage', 'perception', 'peril',
    'periodical', 'permeate', 'permissive', 'perpetual', 'perplex',
    'persecute', 'persistent', 'personnel', 'pessimistic', 'petition',
    'phenomenon', 'philosophy', 'pier', 'pin', 'pioneer', 'pipe', 'pistol',
    'pit', 'pitch', 'plague', 'plaintiff', 'plateau', 'pledge', 'plight',
    'plot', 'plug', 'plunge', 'poetry', 'poison', 'polar', 'polish',
    'politician', 'poll', 'polymer', 'ponder', 'pool', 'populate',
    'porcelain', 'portable', 'portion', 'portrait', 'pose', 'possess',
    'postpone', 'potent', 'poverty', 'practical', 'praise', 'pray',
    'preach', 'precede', 'precedent', 'precision', 'predict', 'predominant',
    'preface', 'prefer', 'pregnant', 'prejudice', 'preliminary', 'premier',
    'premise', 'premium', 'prescription', 'preside', 'presumably', 'presume',
    'pretend', 'prevail', 'prevalent', 'previous', 'prick', 'prime',
    'primitive', 'principal', 'prior', 'priority', 'prison', 'prize',
    'probability', 'procedure', 'proceed', 'processor', 'profession',
    'professional', 'profile', 'profound', 'prohibit', 'prolong',
    'prominent', 'prompt', 'propel', 'proportion', 'proposal', 'propose',
    'prosecute', 'prospect', 'prosper', 'protein', 'protest', 'protocol',
    'prototype', 'proverb', 'provoke', 'prudent', 'psychiatric',
    'psychology', 'publicity', 'puff', 'punch', 'punishment', 'purify',
    'pursue', 'pursuit', 'puzzle', 'qualify', 'quantify', 'quarter',
    'quest', 'questionnaire', 'queue', 'quota', 'quote', 'radiate',
    'radical', 'radius', 'rage', 'raid', 'rally', 'random', 'rank', 'rap',
    'rare', 'rating', 'ratio', 'rational', 'reaction', 'readily',
    'realistic', 'reap', 'reassure', 'rebel', 'receipt', 'reception',
    'recipe', 'reckless', 'reckon', 'reclaim', 'reconcile', 'reconstruct',
    'recreation', 'recruit', 'rectify', 'recur', 'redeem', 'redundant',
    'refine', 'refrain', 'refresh', 'refuge', 'refute', 'regard',
    'regardless', 'regime', 'regulate', 'reluctant', 'remarkable',
    'remedy', 'remote', 'removal', 'render', 'renew', 'renovate', 'repel',
    'repent', 'reproduce', 'reputation', 'rescue', 'resent', 'resolution',
    'resort', 'respectable', 'respective', 'respond', 'response',
    'restless', 'restore', 'restrain', 'restrict', 'resume', 'retail',
    'retain', 'retell', 'retreat', 'retrieve', 'retrospect', 'reverse',
    'revise', 'revolt', 'rhythm', 'ribbon', 'ridge', 'ridiculous', 'rifle',
    'rift', 'rigid', 'riot', 'rip', 'ripe', 'roam', 'roar', 'robust',
    'rocket', 'romance', 'rot', 'rotate', 'rotten', 'rough', 'rouse',
    'route', 'routine', 'royal', 'rubber', 'rude', 'ruin', 'ruler',
    'rumor', 'rust', 'sacrifice', 'saddle', 'safari', 'salad', 'salary',
    'salient', 'salute', 'sanction', 'saturate', 'scale', 'scan',
    'scandal', 'scarce', 'scare', 'scatter', 'scent', 'scheme', 'scholar',
    'scholarship', 'scope', 'scorn', 'scrape', 'scratch', 'screw', 'script',
    'scrutiny', 'seal', 'seam', 'secular', 'sector', 'sediment', 'seduce',
    'segment', 'seize', 'select', 'selfish', 'sensible', 'sentiment',
    'sequence', 'serial', 'sermon', 'servant', 'session', 'setback',
    'setting', 'shade', 'shadow', 'shaft', 'shallow', 'shame', 'shatter',
    'sheer', 'sheet', 'shelter', 'shiver', 'shortage', 'shorthand',
    'shower', 'shrewd', 'shrug', 'shutter', 'shuttle', 'sidewalk', 'sigh',
    'significant', 'silk', 'silver', 'simulate', 'simultaneous', 'sin',
    'sincere', 'singular', 'sip', 'skeleton', 'skeptical', 'sketch', 'skip',
    'slack', 'slap', 'slaughter', 'slender', 'slice', 'slide', 'slight',
    'slim', 'slip', 'slogan', 'slope', 'slot', 'slum', 'smash', 'smog',
    'smuggle', 'snack', 'snap', 'sniff', 'snapshot', 'snob', 'snowy',
    'soar', 'sober', 'socialist', 'socket', 'soda', 'soften', 'solar',
    'solid', 'solitary', 'solo', 'soluble', 'sophisticated', 'sore',
    'sorrow', 'southward', 'sovereign', 'sow', 'span', 'spare', 'spark',
    'specialize', 'species', 'specify', 'spectacle', 'spectrum',
    'speculate', 'spill', 'spin', 'spiral', 'spite', 'splash', 'sponsor',
    'spontaneous', 'spray', 'spur', 'spy', 'squad', 'squeeze', 'stable',
    'stadium', 'staff', 'stain', 'staircase', 'stake', 'stale', 'stalk',
    'stall', 'stamp', 'standpoint', 'startle', 'statistical', 'statistics',
    'statue', 'status', 'steak', 'steer', 'stem', 'stereo', 'stereotype',
    'stern', 'stiff', 'stimulus', 'sting', 'stir', 'stomach', 'stone',
    'stoop', 'storage', 'storey', 'straightforward', 'strain', 'strand',
    'stranger', 'strategic', 'strategy', 'straw', 'stream', 'strengthen',
    'stress', 'stretch', 'strict', 'strike', 'strip', 'stroke', 'stroll',
    'struggle', 'studio', 'stumble', 'stun', 'subjective', 'submarine',
    'subordinate', 'subscribe', 'subsequent', 'subsidy', 'substance',
    'substantial', 'substitute', 'subtle', 'subtract', 'suburb',
    'successive', 'successor', 'suicide', 'sum', 'summary', 'summit',
    'summon', 'superb', 'superior', 'supervise', 'supplement', 'suppress',
    'supreme', 'surge', 'surplus', 'survey', 'survival', 'survive',
    'suspect', 'suspend', 'suspense', 'suspicious', 'sustain', 'swallow',
    'swamp', 'swarm', 'swear', 'sweep', 'swell', 'swift', 'swing',
    'symptom', 'syndrome', 'synthesis', 'systematic', 'tackle', 'tactics',
    'tag', 'tame', 'tan', 'tap', 'target', 'tariff', 'taste', 'taxpayer',
    'tease', 'temper', 'temperament', 'temple', 'tempt', 'tenant',
    'tendency', 'tense', 'tentative', 'terminal', 'territory', 'terror',
    'testify', 'textile', 'texture', 'theater', 'theft', 'theme', 'thereby',
    'thirst', 'threshold', 'thrill', 'thrive', 'throat', 'throne', 'thrust',
    'thumb', 'tick', 'ticket', 'tide', 'timber', 'timid', 'tissue', 'toast',
    'tobacco', 'tolerance', 'tolerant', 'toll', 'tomato', 'tongue', 'token',
    'tolerate', 'torrent', 'torture', 'toss', 'tough', 'tournament',
    'toxic', 'tractor', 'tragedy', 'trail', 'transition', 'translate',
    'transmission', 'transmit', 'transparent', 'traverse', 'treasure',
    'treaty', 'tremendous', 'trend', 'triangle', 'tribe', 'trigger', 'trim',
    'triumph', 'trivial', 'troop', 'tropical', 'troublesome', 'trumpet',
    'trunk', 'trustee', 'tube', 'tunnel', 'turbulent', 'turnover', 'twist',
    'ultimate', 'unanimous', 'unaware', 'uncomfortable', 'unconditional',
    'unconscious', 'underestimate', 'undergo', 'underground', 'underlie',
    'undermine', 'underneath', 'understandable', 'undertake',
    'unemployment', 'unexpected', 'unfavorable', 'unfold', 'unforeseen',
    'unfortunate', 'unify', 'unique', 'universal', 'universe', 'unknown',
    'unlikely', 'unload', 'unreasonable', 'unrest', 'unstable',
    'unsuccessful', 'unusual', 'update', 'upgrade', 'uphold', 'upright',
    'upward', 'urban', 'urgent', 'usage', 'utilize', 'vague', 'valve',
    'vanish', 'variable', 'variation', 'variety', 'vast', 'veil',
    'velocity', 'venture', 'verify', 'versatile', 'verse', 'version',
    'vertical', 'vessel', 'veteran', 'vibrate', 'vicious', 'video',
    'viewpoint', 'violate', 'violation', 'violence', 'visible', 'vision',
    'vital', 'vitamin', 'vivid', 'vocational', 'void', 'volcano',
    'volunteer', 'vulnerable', 'wage', 'waist', 'ward', 'warehouse',
    'warfare', 'warrant', 'warrior', 'wary', 'wavelength', 'weary',
    'weave', 'wedding', 'weep', 'weld', 'whale', 'whereby', 'wherever',
    'whisper', 'whistle', 'wholehearted', 'wicked', 'widen', 'wildlife',
    'willing', 'willingness', 'witness', 'withdraw', 'wolf', 'wonder',
    'wooden', 'workshop', 'worldwide', 'wrap', 'wreck', 'wrestle',
    'wrinkle', 'wrist'
]))

# 托福词汇 (TOEFL) - 在六级基础上扩展
TOEFL_WORDS = CET6_WORDS.union(set([
    'abate', 'abdomen', 'aberrant', 'abet', 'abide', 'abode', 'abort',
    'abound', 'abrasion', 'abreast', 'abridge', 'abrogate', 'abscond',
    'abstain', 'abstruse', 'accelerate', 'accessible', 'accidental',
    'acclaim', 'acclimatize', 'accommodation', 'accreditation', 'accumulate',
    'accuracy', 'achievement', 'acidic', 'acoustic', 'acquisition',
    'actionable', 'activism', 'adaptable', 'adaptive', 'addendum',
    'addict', 'addiction', 'additive', 'addressable', 'adjacent',
    'adjudicate', 'adjunct', 'admission', 'admonish', 'adorn', 'adrift',
    'adulterate', 'advent', 'adverse', 'advertising', 'advocacy', 'aerial',
    'aerobic', 'aerospace', 'affable', 'affirmation', 'affliction',
    'affluent', 'aggravate', 'aggregate', 'agile', 'agitation', 'agnostic',
    'agonize', 'airborne', 'aisle', 'alchemy', 'alcoholic', 'alert',
    'algae', 'alien', 'alienate', 'alignment', 'alimentary', 'allergic',
    'alliance', 'allocation', 'alloy', 'alphabetical', 'alteration',
    'alternative', 'altruistic', 'amalgam', 'ambient', 'ambiguous',
    'ambulatory', 'amenable', 'amendment', 'amino', 'amnesia', 'amorphous',
    'amplify', 'analogous', 'analogy', 'anarchic', 'anatomy', 'ancestor',
    'anchor', 'anecdote', 'anemia', 'anesthetic', 'angelic', 'anger',
    'angular', 'anhydrous', 'animosity', 'annals', 'annoyance', 'annual',
    'anomaly', 'anonymous', 'antagonism', 'antecedent', 'anterior',
    'anthropology', 'antibiotic', 'antibody', 'anticipate', 'antidote',
    'antigen', 'antipathy', 'antiquity', 'antiviral', 'apex', 'aphasia',
    'aphorism', 'apocalypse', 'apocryphal', 'apolitical', 'apology',
    'apoptosis', 'apparatus', 'apparel', 'apparent', 'appease', 'appellation',
    'appendix', 'appetite', 'applaud', 'applicable', 'appoint',
    'appraisal', 'apprehension', 'apprentice', 'aptitude', 'aquatic',
    'arachnid', 'arbiter', 'arbitrary', 'arbitrate', 'arcade', 'archaic',
    'archetype', 'architectural', 'ardent', 'arena', 'argot', 'arid',
    'armament', 'aroma', 'aromatic', 'arraign', 'arrangement', 'arrest',
    'arrogant', 'arsenic', 'arson', 'artery', 'arthritis', 'articulate',
    'artifact', 'artifice', 'ascend', 'ascetic', 'ascribe', 'aseptic',
    'ashen', 'asylum', 'asymmetric', 'atlas', 'atmospheric', 'atrocity',
    'attain', 'attendant', 'attire', 'attribute', 'atypical', 'audible',
    'audition', 'augment', 'aura', 'auspicious', 'authentic', 'authorize',
    'autobiography', 'autopsy', 'autopilot', 'autonomous', 'avail',
    'averse', 'aversion', 'avert', 'aviation', 'avid', 'avow', 'awry',
    'babble', 'backlash', 'bacteria', 'bacterium', 'badger', 'baggage',
    'bail', 'bale', 'balk', 'ballast', 'balm', 'balmy', 'banal', 'bandage',
    'banish', 'banquet', 'barbaric', 'barbiturate', 'barge', 'barium',
    'bark', 'barometer', 'baron', 'barren', 'barricade', 'baseball',
    'bash', 'basin', 'bask', 'bastion', 'bathe', 'battery', 'bauxite',
    'bayou', 'beacon', 'bead', 'beak', 'bearable', 'beatify', 'beckon',
    'bedlam', 'befall', 'befit', 'begrudge', 'behalf', 'behave', 'behavioral',
    'belabor', 'belated', 'belch', 'believer', 'belittle', 'belligerent',
    'bellows', 'belly', 'belonging', 'benchmark', 'benediction',
    'beneficent', 'benign', 'bent', 'bereave', 'beseech', 'beset',
    'besiege', 'bestial', 'bestow', 'betray', 'betroth', 'bevy', 'bias',
    'bibliography', 'bid', 'bifurcate', 'bigot', 'bile', 'bilingual',
    'binoculars', 'biopsy', 'birch', 'bisect', 'bizarre', 'blackmail',
    'blanch', 'bland', 'blare', 'blast', 'blaze', 'bleak', 'blemish',
    'blend', 'blight', 'blindness', 'bliss', 'blitz', 'bloom', 'blossom',
    'blotch', 'blouse', 'bluff', 'blunder', 'blunt', 'blur', 'blurt',
    'blush', 'boast', 'boggle', 'bold', 'bombard', 'bondage', 'bonfire',
    'bonus', 'boo', 'boomerang', 'boon', 'boost', 'booth', 'bore', 'bosom',
    'botanical', 'botany', 'bounce', 'boundary', 'bout', 'bowel', 'boxer',
    'boycott', 'brace', 'bracket', 'brad', 'braggart', 'braid', 'brainstem',
    'bramble', 'branch', 'brandish', 'brash', 'brass', 'brave', 'breach',
    'breakthrough', 'breathless', 'breed', 'breeze', 'bribe', 'brick',
    'bridegroom', 'bridge', 'brief', 'briefcase', 'brigade', 'brink',
    'brisk', 'bristle', 'brittle', 'brittle', 'broach', 'broadcast',
    'brochure', 'broken', 'bronchial', 'bronze', 'brood', 'brook', 'broom',
    'brotherhood', 'browse', 'bruise', 'brunt', 'brush', 'brute', 'bubble',
    'buck', 'bucket', 'buckle', 'bud', 'budget', 'buffalo', 'buffer',
    'buffet', 'bugle', 'build', 'bulb', 'bulge', 'bulk', 'bull', 'bullet',
    'bulletin', 'bully', 'bumper', 'bump', 'bunch', 'bundle', 'bungalow',
    'bureau', 'bureaucracy', 'burglar', 'burial', 'burner', 'bush', 'business',
    'butcher', 'butterfly', 'button', 'buzz', 'cabin', 'cable', 'cactus',
    'cadet', 'cafeteria', 'caffeine', 'cage', 'calendar', 'calf', 'calorie',
    'camera', 'camp', 'campaign', 'campus', 'canal', 'canary', 'candidate',
    'cannon', 'canoe', 'canvas', 'canyon', 'cap', 'capacitor', 'cape', 'captain',
    'captive', 'capture', 'caravan', 'carbon', 'cardboard', 'carefree', 'cargo',
    'carrot', 'cart', 'cartoon', 'carve', 'cascade', 'cashier', 'cassette',
    'castle', 'casual', 'catastrophe', 'catalog', 'catalyst', 'cathedral',
    'cathedral', 'category', 'cater', 'catholic', 'cavern', 'cavity', 'cease',
    'celebrate', 'celery', 'cellar', 'cellphone', 'cement', 'census', 'cent',
    'centimeter', 'central', 'century', 'ceramic', 'cereal', 'ceremony',
    'certificate', 'chamber', 'champion', 'championship', 'channel', 'chapel',
    'chapter', 'charcoal', 'charge', 'charm', 'chart', 'charter', 'chase',
    'cheek', 'cheerful', 'chemical', 'cherry', 'chess', 'chest', 'chew',
    'chicken', 'chief', 'childhood', 'chill', 'chimney', 'chin', 'chip',
    'chocolate', 'choke', 'chord', 'chore', 'christian', 'chromosome',
    'chronic', 'chunk', 'circus', 'citizen', 'city', 'civil', 'clap',
    'clarify', 'clarity', 'clash', 'clasp', 'classic', 'classroom', 'clause',
    'claw', 'clay', 'cleaner', 'clerk', 'click', 'client', 'climate',
    'clinic', 'clipboard', 'clock', 'clone', 'closet', 'cluster', 'clutch',
    'coach', 'coal', 'coarse', 'coast', 'cocoa', 'code', 'coffee', 'cognitive',
    'coherent', 'coincide', 'collaborate', 'collapse', 'colleague', 'collective',
    'college', 'collide', 'colon', 'colony', 'colorful', 'combat', 'comic',
    'comma', 'command', 'comment', 'commercial', 'commission', 'commit',
    'committee', 'commonplace', 'community', 'company', 'comparative',
    'compatible', 'compel', 'compensate', 'compile', 'complex', 'complicated',
    'component', 'compose', 'comprehend', 'compromise', 'computer',
    'concentrate', 'concept', 'concert', 'conclude', 'concrete', 'condition',
    'conductor', 'conference', 'confident', 'confirm', 'conflict', 'confusion',
    'congress', 'connect', 'consequence', 'conservative', 'consider',
    'consistent', 'construct', 'consult', 'consume', 'contact', 'contain',
    'content', 'contest', 'context', 'contract', 'contrast', 'contribute',
    'control', 'convention', 'conversation', 'convert', 'convey', 'convince',
    'cooperate', 'coordinate', 'cop', 'cope', 'copper', 'copyright', 'corn',
    'corner', 'corporate', 'correct', 'correspond', 'corridor', 'costume',
    'cottage', 'cotton', 'cough', 'council', 'counsel', 'counter',
    'counterpart', 'countryside', 'couple', 'courage', 'court', 'cousin',
    'coverage', 'cow', 'coward', 'crack', 'craft', 'crane', 'crash',
    'crawl', 'crazy', 'cream', 'credit', 'creep', 'crew', 'crime', 'criminal',
    'crisis', 'critic', 'criticize', 'crop', 'cross', 'crowd', 'cruel',
    'cruise', 'crush', 'crystal', 'cube', 'cubic', 'cuisine', 'culture',
    'cupboard', 'curious', 'currency', 'current', 'curriculum', 'curtain',
    'custom', 'customer', 'cycle', 'cylinder', 'dad', 'daily', 'dairy',
    'dam', 'damage', 'dance', 'danger', 'daring', 'darkness', 'dash',
    'database', 'daughter', 'dawn', 'daylight', 'dead', 'deaf', 'deal',
    'dealer', 'dear', 'death', 'debate', 'debt', 'decade', 'deceive',
    'December', 'decide', 'decline', 'decorate', 'decrease', 'dedicated',
    'deep', 'deer', 'defeat', 'defense', 'deficit', 'define', 'definite',
    'definition', 'degree', 'delay', 'deliver', 'demand', 'democracy',
    'demonstrate', 'deny', 'depart', 'depend', 'depict', 'deposit',
    'depress', 'depth', 'derive', 'descend', 'describe', 'desert',
    'design', 'desire', 'desk', 'destroy', 'detail', 'detect', 'determine',
    'develop', 'device', 'devote', 'diagnose', 'diagram', 'dialogue',
    'diamond', 'diary', 'dictate', 'dictionary', 'die', 'diet', 'differ',
    'difficult', 'digital', 'dignity', 'dilemma', 'dinner', 'direct',
    'direction', 'director', 'dirt', 'disappear', 'disappoint', 'disaster',
    'discard', 'discharge', 'discipline', 'discover', 'discuss', 'disease',
    'dismiss', 'display', 'distance', 'distinct', 'distinguish', 'distribute',
    'divide', 'division', 'doctor', 'document', 'dog', 'doll', 'dollar',
    'domain', 'domestic', 'dominant', 'donate', 'door', 'double', 'doubt',
    'draft', 'dragon', 'drama', 'draw', 'dream', 'dress', 'drink', 'drive',
    'driver', 'drop', 'drug', 'dry', 'duck', 'due', 'dull', 'dumb',
    'dump', 'durable', 'duration', 'dust', 'duty', 'dwarf', 'dynamic',
    'eagle', 'ear', 'early', 'earn', 'earth', 'earthquake', 'ease',
    'east', 'easy', 'echo', 'ecology', 'economic', 'economy', 'edge',
    'education', 'effect', 'efficient', 'effort', 'egg', 'eight', 'either',
    'elaborate', 'electric', 'electricity', 'electronic', 'element',
    'elephant', 'elevator', 'eliminate', 'elite', 'else', 'email',
    'emerge', 'emergency', 'emotion', 'emperor', 'employ', 'empty',
    'enable', 'encourage', 'end', 'enemy', 'energy', 'engine', 'engineer',
    'enjoy', 'enormous', 'enough', 'enter', 'enterprise', 'entertain',
    'enthusiasm', 'entire', 'entrance', 'environment', 'equal', 'equipment',
    'error', 'escape', 'especially', 'essay', 'essential', 'establish',
    'estimate', 'evaluate', 'evaporate', 'even', 'evening', 'event',
    'eventually', 'evidence', 'evident', 'evil', 'evolution', 'exact',
    'examine', 'example', 'excellent', 'except', 'exchange', 'exclude',
    'excuse', 'execute', 'exercise', 'exhibit', 'expand', 'expect',
    'expense', 'experience', 'experiment', 'expert', 'explain', 'explore',
    'export', 'express', 'extend', 'external', 'extra', 'extreme',
    'eye', 'eyebrow', 'fabric', 'face', 'factor', 'factory', 'fade',
    'faint', 'fair', 'faith', 'fall', 'false', 'family', 'famous',
    'fan', 'fancy', 'fantasy', 'far', 'farm', 'fashion', 'fast',
    'father', 'fear', 'feature', 'federal', 'feed', 'feel', 'female',
    'fence', 'ferry', 'fertile', 'festival', 'fetch', 'fever', 'fiber',
    'fiction', 'field', 'fierce', 'file', 'filter', 'final', 'finance',
    'find', 'fine', 'finger', 'finish', 'fire', 'firm', 'fish', 'fit',
    'flag', 'flame', 'flash', 'flesh', 'flexible', 'flight', 'float',
    'flood', 'floor', 'flour', 'flow', 'flower', 'fly', 'focus',
    'fog', 'fold', 'follow', 'food', 'fool', 'foot', 'football',
    'forbid', 'force', 'forecast', 'foreign', 'forest', 'forget',
    'forgive', 'fork', 'form', 'formal', 'format', 'former', 'fortune',
    'forward', 'fountain', 'fox', 'frame', 'free', 'freedom', 'freeze',
    'fresh', 'friction', 'friend', 'fridge', 'frog', 'front', 'fruit',
    'fuel', 'full', 'fun', 'function', 'fund', 'fundamental', 'funny',
    'furniture', 'future', 'gable', 'gain', 'galaxy', 'gallery', 'game',
    'garden', 'garlic', 'gas', 'gate', 'gather', 'general', 'generate',
    'generation', 'genius', 'gentle', 'genuine', 'geography', 'geometry',
    'germ', 'ghost', 'giant', 'gift', 'girl', 'glad', 'glass', 'global',
    'globe', 'glove', 'glow', 'goat', 'god', 'gold', 'golden', 'good',
    'govern', 'government', 'grace', 'grade', 'gradual', 'graduate',
    'grain', 'grand', 'grant', 'grass', 'great', 'green', 'grief',
    'ground', 'group', 'grow', 'growth', 'guard', 'guess', 'guest',
    'guide', 'guilt', 'guitar', 'gun', 'gust', 'habit', 'hair', 'half',
    'hall', 'hammer', 'hand', 'handle', 'hang', 'happen', 'happy', 'hard',
    'harm', 'harvest', 'hate', 'have', 'hay', 'head', 'heal', 'health',
    'healthy', 'hear', 'heart', 'heat', 'heavy', 'height', 'helicopter',
    'hell', 'help', 'hen', 'herb', 'hero', 'hide', 'high', 'hill',
    'himself', 'history', 'hit', 'hold', 'hole', 'holiday', 'home',
    'honest', 'honor', 'hope', 'horn', 'horse', 'hospital', 'host',
    'hot', 'hotel', 'hour', 'house', 'howl', 'huge', 'human', 'humor',
    'hundred', 'hunger', 'hunt', 'hurry', 'hurt', 'husband', 'hydrogen',
    'ice', 'idea', 'identify', 'ignore', 'ill', 'illegal', 'image',
    'imagine', 'immediate', 'import', 'impossible', 'improve', 'include',
    'income', 'increase', 'independent', 'index', 'individual', 'industrial',
    'industry', 'influence', 'inform', 'information', 'initial', 'inject',
    'injury', 'inside', 'insist', 'install', 'instance', 'instead',
    'institute', 'instruction', 'instrument', 'insurance', 'intelligence',
    'intend', 'interest', 'international', 'internet', 'interval',
    'interview', 'introduce', 'invent', 'investment', 'involve', 'iron',
    'island', 'issue', 'ivory', 'jacket', 'jail', 'jam', 'jar', 'jaw',
    'jealous', 'jeans', 'jewel', 'job', 'join', 'joint', 'joke', 'journey',
    'joy', 'judge', 'juice', 'jump', 'jungle', 'junior', 'jury', 'just',
    'keep', 'kettle', 'key', 'keyboard', 'kick', 'kid', 'kill', 'kind',
    'king', 'kitchen', 'knee', 'knife', 'knock', 'knowledge', 'label',
    'labor', 'lack', 'ladder', 'lady', 'lake', 'lamp', 'land', 'language',
    'large', 'last', 'late', 'laugh', 'law', 'layer', 'lead', 'leader',
    'learn', 'lease', 'least', 'leave', 'lecture', 'left', 'leg', 'legal',
    'lemon', 'length', 'lesson', 'let', 'letter', 'level', 'library',
    'license', 'life', 'lift', 'light', 'like', 'limit', 'line', 'link',
    'lion', 'lip', 'liquid', 'list', 'literature', 'little', 'live',
    'load', 'local', 'lock', 'long', 'look', 'loose', 'lose', 'loss',
    'lot', 'love', 'low', 'luck', 'lunch', 'machine', 'magazine', 'magic',
    'mail', 'main', 'maintain', 'major', 'make', 'male', 'man', 'manage',
    'manner', 'manufacture', 'many', 'map', 'market', 'marriage', 'material',
    'math', 'matter', 'may', 'meal', 'mean', 'measure', 'meat', 'media',
    'medical', 'medicine', 'meet', 'member', 'memory', 'mental', 'menu',
    'merchant', 'metal', 'method', 'middle', 'might', 'military', 'milk',
    'million', 'mind', 'mine', 'minister', 'minor', 'minute', 'mirror',
    'miss', 'mission', 'mistake', 'mix', 'model', 'modern', 'moment',
    'money', 'monitor', 'month', 'moon', 'more', 'morning', 'mother',
    'motion', 'motor', 'mountain', 'mouse', 'mouth', 'move', 'movie',
    'much', 'mud', 'music', 'must', 'my', 'myself', 'nail', 'name',
    'nation', 'natural', 'nature', 'near', 'neck', 'need', 'negative',
    'neighbor', 'neither', 'nerve', 'network', 'neutral', 'never',
    'new', 'news', 'newspaper', 'next', 'night', 'nine', 'no', 'noble',
    'noise', 'nominate', 'none', 'normal', 'north', 'nose', 'not',
    'nothing', 'notice', 'novel', 'now', 'nuclear', 'number', 'nurse',
    'nut', 'oak', 'obey', 'object', 'obvious', 'occasion', 'occur',
    'ocean', 'offer', 'office', 'officer', 'official', 'oil', 'old',
    'once', 'one', 'only', 'open', 'opinion', 'opportunity', 'opposite',
    'option', 'order', 'ordinary', 'organ', 'organic', 'organize', 'origin',
    'original', 'other', 'otherwise', 'our', 'out', 'outside', 'over',
    'owner', 'oxygen', 'pace', 'pack', 'page', 'pain', 'paint', 'pair',
    'palace', 'pale', 'pan', 'paper', 'parent', 'park', 'part', 'party',
    'pass', 'passage', 'passenger', 'past', 'pat', 'path', 'pattern', 'pause',
    'pay', 'peace', 'peak', 'pen', 'pencil', 'people', 'percent', 'perfect',
    'perform', 'perhaps', 'period', 'permanent', 'permission', 'person',
    'personal', 'phone', 'photo', 'physical', 'pick', 'picture', 'pie',
    'piece', 'pig', 'pilot', 'pine', 'pink', 'pipe', 'place', 'plan',
    'plant', 'plate', 'play', 'pleasant', 'please', 'plenty', 'plural',
    'plus', 'pocket', 'poem', 'poet', 'poetry', 'point', 'poison', 'police',
    'policy', 'politics', 'poll', 'pond', 'pool', 'poor', 'popular',
    'population', 'port', 'position', 'positive', 'possible', 'post',
    'pot', 'potential', 'power', 'practical', 'practice', 'prepare',
    'present', 'press', 'pressure', 'prevent', 'price', 'pride', 'primary',
    'print', 'private', 'prize', 'problem', 'process', 'produce', 'product',
    'profit', 'program', 'progress', 'project', 'promise', 'promote', 'proper',
    'protect', 'prove', 'provide', 'public', 'publish', 'pull', 'pulse',
    'pump', 'punish', 'purchase', 'pure', 'purpose', 'push', 'put',
    'quality', 'quantity', 'quarter', 'question', 'quick', 'quiet', 'quit',
    'quite', 'race', 'radio', 'rail', 'rain', 'raise', 'range', 'rapid',
    'rate', 'rather', 'raw', 'reach', 'read', 'ready', 'real', 'reality',
    'realize', 'reason', 'receive', 'recent', 'recognize', 'record',
    'recover', 'reduce', 'refer', 'reflect', 'reform', 'refuse', 'region',
    'register', 'regular', 'regulate', 'reject', 'relax', 'release',
    'relevant', 'relief', 'religion', 'rely', 'remain', 'remember', 'remind',
    'remove', 'replace', 'reply', 'report', 'represent', 'reproduce',
    'request', 'require', 'research', 'resemble', 'reserve', 'resident',
    'resist', 'resolve', 'resource', 'respect', 'respond', 'responsible',
    'rest', 'result', 'return', 'review', 'revolution', 'reward', 'rich',
    'ride', 'right', 'ring', 'rise', 'risk', 'river', 'road', 'rock',
    'role', 'roll', 'roof', 'room', 'root', 'rope', 'rose', 'rough', 'round',
    'route', 'routine', 'row', 'royal', 'rub', 'rubber', 'rule', 'run',
    'rush', 'sad', 'safe', 'safety', 'sail', 'sale', 'salt', 'same',
    'sand', 'satellite', 'satisfy', 'save', 'say', 'scale', 'school',
    'science', 'scientist', 'score', 'sea', 'search', 'season', 'seat',
    'second', 'secret', 'section', 'security', 'see', 'seed', 'seek',
    'seem', 'sell', 'send', 'sense', 'separate', 'series', 'serious',
    'serve', 'service', 'set', 'settle', 'seven', 'several', 'shade',
    'shadow', 'shake', 'share', 'sharp', 'sheep', 'sheet', 'shelf',
    'shell', 'shift', 'shine', 'ship', 'shirt', 'shock', 'shoe', 'shoot',
    'shop', 'short', 'should', 'shoulder', 'shout', 'show', 'sick', 'side',
    'sign', 'signal', 'silence', 'silent', 'simple', 'since', 'sing',
    'sink', 'size', 'skill', 'skin', 'sky', 'sleep', 'slight', 'slow',
    'small', 'smell', 'smile', 'smoke', 'smooth', 'snake', 'snow', 'so',
    'social', 'society', 'soft', 'soil', 'solar', 'soldier', 'solid',
    'solution', 'solve', 'some', 'son', 'song', 'soon', 'sorry', 'sound',
    'source', 'south', 'space', 'speak', 'special', 'species', 'speed',
    'spell', 'spend', 'spin', 'spirit', 'split', 'spoil', 'spread',
    'spring', 'square', 'stage', 'stair', 'stand', 'standard', 'star',
    'start', 'state', 'station', 'stay', 'step', 'stick', 'still',
    'stock', 'stop', 'store', 'storm', 'story', 'straight', 'strange',
    'street', 'strength', 'stretch', 'strike', 'strong', 'structure',
    'student', 'study', 'stuff', 'style', 'subject', 'succeed', 'success',
    'such', 'sudden', 'suffer', 'suggest', 'suit', 'summer', 'sun', 'super',
    'supply', 'support', 'suppose', 'sure', 'surface', 'system', 'table',
    'tail', 'take', 'talk', 'task', 'tax', 'tea', 'teach', 'teacher',
    'team', 'technology', 'telephone', 'television', 'tell', 'temperature',
    'ten', 'term', 'test', 'than', 'that', 'the', 'theater', 'their',
    'them', 'then', 'theory', 'there', 'therefore', 'these', 'they', 'thin',
    'thing', 'think', 'third', 'this', 'those', 'though', 'thought',
    'three', 'through', 'throw', 'thus', 'time', 'tiny', 'tip', 'tire',
    'title', 'to', 'today', 'together', 'tomorrow', 'tone', 'too', 'tool',
    'top', 'topic', 'tower', 'town', 'toy', 'trace', 'track', 'trade',
    'traffic', 'train', 'transfer', 'transform', 'transport', 'travel',
    'treat', 'tree', 'trial', 'trip', 'trouble', 'true', 'trust', 'truth',
    'try', 'tube', 'turn', 'twist', 'two', 'type', 'under', 'understand',
    'union', 'unit', 'university', 'until', 'up', 'upon', 'use', 'usual',
    'value', 'various', 'vegetable', 'vehicle', 'very', 'victory', 'view',
    'village', 'visit', 'voice', 'volume', 'vote', 'walk', 'wall', 'want',
    'war', 'warm', 'wash', 'waste', 'watch', 'water', 'wave', 'way',
    'weather', 'week', 'weigh', 'welcome', 'well', 'west', 'what', 'wheel',
    'when', 'where', 'whether', 'which', 'while', 'white', 'who', 'whole',
    'whom', 'whose', 'why', 'wide', 'wife', 'wild', 'will', 'win', 'wind',
    'window', 'wine', 'winter', 'with', 'within', 'without', 'woman',
    'wood', 'word', 'work', 'world', 'worry', 'write', 'writer',
    'wrong', 'year', 'yellow', 'yes', 'yesterday', 'you', 'young', 'your',
    'youth', 'zero'
]))

# GRE词汇 (GRE) - 在托福基础上扩展，约300个高频GRE词汇
GRE_WORDS = TOEFL_WORDS.union(set([
    'aberrant', 'abnegate', 'abstemious', 'accolade', 'acrimony', 'admonish', 'adulation', 'aesthetic',
    'aggrandize', 'alacrity', 'amalgamate', 'ambivalent', 'amenable', 'amorphous', 'anachronism',
    'anathema', 'anomaly', 'antipathy', 'apathy', 'appease', 'apprehensive', 'arcane', 'arduous',
    'articulate', 'ascetic', 'assiduous', 'asthenic', 'atrophy', 'austere', 'avarice', 'bellicose',
    'benevolent', 'bombastic', 'boorish', 'burgeon', 'burnish', 'buttress', 'cacophony', 'cajole',
    'calumny', 'candor', 'capricious', 'castigate', 'catalyst', 'caustic', 'chicanery', 'chronology',
    'churlish', 'circumspect', 'clandestine', 'coalesce', 'cogent', 'commensurate', 'compendium',
    'complaisant', 'conciliatory', 'conflagration', 'connoisseur', 'contentious', 'contrite', 'conundrum',
    'corroborate', 'coruscate', 'credulous', 'culpable', 'cupidity', 'cursory', 'dank', 'daunt',
    'debacle', 'decorum', 'deference', 'delineate', 'deleterious', 'demagogue', 'denigrate', 'deprecate',
    'deride', 'derivative', 'desiccate', 'desultory', 'diatribe', 'dichotomy', 'didactic', 'diffident',
    'digress', 'dilatory', 'dirge', 'disabuse', 'discriminating', 'disingenuous', 'disparage', 'disparate',
    'dissemble', 'disseminate', 'divisive', 'docile', 'dogmatic', 'dormant', 'duplicity', 'ebullient',
    'eclectic', 'edify', 'efficacy', 'effrontery', 'elegy', 'elucidate', 'elusive', 'emulate',
    'encomium', 'endemic', 'enervate', 'engender', 'enigma', 'ennui', 'ephemeral', 'epiphany',
    'equanimity', 'equivocate', 'erudite', 'esoteric', 'ethereal', 'euphemism', 'exacerbate', 'excoriate',
    'exculpate', 'exegesis', 'exemplar', 'exigency', 'exonerate', 'expatiate', 'extant', 'extrapolate',
    'facetious', 'fallacious', 'fatuous', 'fawn', 'feckless', 'felonious', 'fervent', 'flagrant',
    'flout', 'foment', 'forbearance', 'fortuitous', 'fractious', 'frenetic', 'frugal', 'furor',
    'gainsay', 'garrulous', 'germane', 'glib', 'gossamer', 'grandiloquent', 'gratuitous', 'gregarious',
    'hackneyed', 'halcyon', 'harangue', 'harbinger', 'hedonist', 'heresy', 'hermetic', 'heterodox',
    'hirsute', 'homogeneous', 'hubris', 'iconoclast', 'idiosyncrasy', 'ignominious', 'immutable',
    'impecunious', 'imperturbable', 'impetuous', 'implacable', 'impudent', 'incisive', 'incongruous',
    'incontrovertible', 'incorrigible', 'indifferent', 'indigent', 'indolent', 'ineffable', 'inexorable',
    'ingenuous', 'inimical', 'inimitable', 'innate', 'innocuous', 'inscrutable', 'insidious', 'insipid',
    'intransigent', 'intrepid', 'inure', 'inveterate', 'irreverent', 'itinerant', 'judicious', 'juxtapose',
    'kinetic', 'laconic', 'largesse', 'latent', 'laudable', 'lavish', 'legerdemain', 'lenient',
    'lewd', 'logistical', 'loquacious', 'lucid', 'luminous', 'macerate', 'magnanimous', 'malapropism',
    'malevolent', 'malleable', 'maverick', 'mendacious', 'mercurial', 'meretricious', 'meticulous',
    'misanthrope', 'misconstruct', 'munificent', 'myopic', 'nadir', 'nebulous', 'nefarious', 'negligible',
    'neophyte', 'nocuous', 'nonplussed', 'nostalgia', 'nuance', 'obdurate', 'obfuscate', 'obsequious',
    'obstreperous', 'obviate', 'odious', 'officious', 'ominous', 'omnipotent', 'omniscient', 'onerous',
    'opaque', 'opprobrium', 'oscillate', 'ostentatious', 'panacea', 'panegyric', 'paradigm', 'parsimonious',
    'partiality', 'pathological', 'pedantic', 'penurious', 'percipient', 'peremptory', 'perfunctory',
    'perimeter', 'pernicious', 'perspicacious', 'pervasive', 'phlegmatic', 'pious', 'placate', 'platitude',
    'plausible', 'plethora', 'poignant', 'pragmatic', 'precarious', 'precipitate', 'preclude', 'precocious',
    'predilection', 'preeminent', 'prescient', 'prestigious', 'prevaricate', 'primordial', 'pristine',
    'probity', 'proclivity', 'profligate', 'profound', 'profuse', 'proliferate', 'prolific', 'propensity',
    'propitiate', 'prudent', 'puerile', 'pugnacious', 'pulchritude', 'punctilious', 'quagmire', 'quiescent',
    'quixotic', 'rapacious', 'rationale', 'recalcitrant', 'recondite', 'redoubtable', 'refractory', 'refute',
    'remonstrate', 'renege', 'replete', 'reprobate', 'repudiate', 'rescind', 'reticent', 'revere',
    'rhetoric', 'sacrosanct', 'sagacious', 'salient', 'sanctimonious', 'sanguine', 'sardonic', 'savant',
    'secular', 'sedulous', 'serendipity', 'servile', 'silhouette', 'simulate', 'skeptical', 'soporific',
    'spectrum', 'spurious', 'squalid', 'stigmatize', 'stolid', 'stratagem', 'strident', 'subjugate',
    'subversive', 'succinct', 'sunder', 'supercilious', 'superfluous', 'supplant', 'surreptitious',
    'sustained', 'tacit', 'tangential', 'tautology', 'temerity', 'tendentious', 'tenacious', 'tenuous',
    'terse', 'timorous', 'toady', 'torpid', 'truculent', 'turbid', 'turgid', 'ubiquitous', 'unction',
    'usurp', 'vacillate', 'vapid', 'vehement', 'venal', 'venerate', 'veracious', 'verbose', 'verisimilitude',
    'vernacular', 'vestige', 'vicarious', 'vindicate', 'virtuoso', 'virulent', 'viscid', 'vituperate',
    'vociferous', 'voluble', 'voracious', 'warranted', 'whimsical', 'zephyr'
]))

CET4_ONLY_WORDS = CET4_WORDS - BASIC_WORDS
CET6_ONLY_WORDS = CET6_WORDS - CET4_WORDS - BASIC_WORDS
TOEFL_ONLY_WORDS = TOEFL_WORDS - CET6_WORDS - CET4_WORDS - BASIC_WORDS
GRE_ONLY_WORDS = GRE_WORDS - TOEFL_WORDS - CET6_WORDS - CET4_WORDS - BASIC_WORDS

NEWS_WORD_DIFFICULTY_OVERRIDES = {
    "ally": "CET6",
    "bodycam": "CET6",
    "chancellor": "CET6",
    "drone": "CET6",
    "enrage": "CET6",
    "fatal": "CET6",
    "footage": "CET6",
    "handcuff": "CET6",
    "hatred": "CET6",
    "intensify": "CET6",
    "missile": "CET6",
    "reiterate": "CET6",
    "self-hatred": "TOEFL",
    "stab": "CET6",
    "tragic": "CET6",
    "unprecedented": "TOEFL",
}

# 常用短语和习语
PHRASES = [
    'come to terms with', 'take into account', 'make sense of',
    'shed light on', 'give rise to', 'take advantage of',
    'pay attention to', 'make a difference', 'put forward',
    'carry out', 'bring about', 'account for',
    'take place', 'come up with', 'keep up with',
    'catch up with', 'look forward to', 'get along with',
    'make up for', 'go through with', 'put up with',
    'run out of', 'get away with', 'break away from',
    'look down on', 'take care of', 'make fun of',
    'lose sight of', 'give up on', 'hold on to',
    'let go of', 'stick to', 'point out',
    'figure out', 'work out', 'carry on',
    'go on', 'come on', 'keep on',
    'put on', 'take off', 'turn on',
    'turn off', 'look up', 'look down',
    'look out', 'look into', 'look over',
    'bring up', 'bring down', 'bring out',
    'set up', 'set off', 'set out',
    'take over', 'take in', 'take up',
    'give in', 'give out', 'give away',
    'hand in', 'hand out', 'hand over',
    'pass away', 'pass out', 'pass by',
    'turn up', 'turn down', 'turn out',
    'carry away', 'carry off', 'carry on',
    'get up', 'get down', 'get off',
    'get on', 'get through', 'get around',
    'make up', 'make out', 'make off',
    'break down', 'break up', 'break out',
    'break in', 'break through', 'break off',
    'go back', 'go down', 'go up',
    'go off', 'go out', 'go over',
    'come back', 'come down', 'come out',
    'come in', 'come over', 'come through',
    'fall down', 'fall off', 'fall behind',
    'fall out', 'fall through', 'hold up',
    'hold down', 'hold off', 'keep down',
    'keep out', 'keep up', 'let down',
    'let off', 'let out', 'put down',
    'put out', 'put together', 'run away',
    'run down', 'run off', 'run through',
    'see off', 'see through', 'show up',
    'stay up', 'stay away', 'stay out',
    'take back', 'take down', 'take off',
    'think over', 'think through', 'throw away',
    'throw out', 'touch up', 'try out',
    'wait for', 'wait on', 'wake up',
    'watch out', 'wear out', 'work off',
    'work out', 'write down', 'write off',
    # 介词短语
    'in terms of', 'with respect to', 'on behalf of', 'in favor of', 'due to',
    'because of', 'in addition to', 'as well as', 'by means of', 'in spite of',
    'with regard to', 'for the sake of', 'on account of', 'at the expense of',
    'in the light of', 'by virtue of', 'in consequence of', 'regardless of',
    # 动词短语扩展
    'come about', 'come across', 'come along', 'come apart', 'come around',
    'count on', 'count up', 'count out', 'count in', 'carry over', 'carry through',
    'drop off', 'drop out', 'drop in', 'drop behind', 'drop down',
    'end up', 'end in', 'end up with', 'face up to', 'fall for',
    'feel like', 'fill in', 'fill out', 'find out', 'get across',
    'get ahead', 'get along', 'get around to', 'get away', 'get back',
    'get by', 'get down to', 'get hold of', 'get in', 'get into',
    'get out', 'get over', 'get rid of', 'get through', 'give away',
    'give back', 'give in', 'give out', 'give up', 'go about',
    'go after', 'go ahead', 'go along', 'go around', 'go beyond',
    'go for', 'go in for', 'go into', 'go off', 'go on',
    'go out', 'go over', 'go through', 'go together', 'go with',
    'go without', 'grow up', 'hand in', 'hand out', 'hand over',
    'have on', 'hear about', 'hear from', 'hear of', 'hold back',
    'hold on', 'hold out', 'hold over', 'hold with', 'join in',
    'keep from', 'keep in with', 'keep off', 'keep on', 'keep to',
    'keep up with', 'lay down', 'lay off', 'lay out', 'leave behind',
    'leave off', 'leave out', 'let in', 'let off', 'let out',
    'lie down', 'lie in', 'lie with', 'live off', 'live on',
    'live through', 'live up to', 'look after', 'look ahead', 'look around',
    'look at', 'look back', 'look down on', 'look forward to', 'look in on',
    'look into', 'look on', 'look out for', 'look over', 'look to',
    'look up to', 'make for', 'make off with', 'make out', 'make over',
    'make up for', 'mix up', 'move in', 'move out', 'move on',
    'pass away', 'pass by', 'pass on', 'pass out', 'pass over',
    'pay back', 'pay for', 'pay off', 'pay out', 'pick out',
    'pick up', 'point out', 'pull down', 'pull in', 'pull off',
    'pull out', 'pull together', 'push around', 'push on', 'push over',
    'put across', 'put away', 'put back', 'put by', 'put down to',
    'put in for', 'put off', 'put out', 'put up with', 'put upon',
    'read out', 'read up', 'result in', 'rule out', 'run across',
    'run into', 'run off', 'run out of', 'run to', 'run up against',
    'search for', 'see about', 'see after', 'see into', 'see to',
    'seek out', 'sell off', 'sell out', 'send back', 'send for',
    'send in', 'send out', 'set about', 'set aside', 'set back',
    'set down', 'set forth', 'set in', 'set off', 'set on',
    'set out', 'set up', 'settle down', 'settle for', 'settle in',
    'settle into', 'settle on', 'settle up', 'shake off', 'show off',
    'show out', 'show up', 'shut down', 'shut off', 'shut out',
    'shut up', 'sit down', 'sit in', 'sit out', 'sit through',
    'sit up', 'size up', 'sleep on', 'sleep through', 'slip away',
    'slip in', 'slip into', 'slip out', 'slip up', 'smooth over',
    'snap up', 'stand by', 'stand down', 'stand for', 'stand in',
    'stand out', 'stand up', 'stand up for', 'stand up to', 'start in',
    'start off', 'start on', 'start out', 'start over', 'start up',
    'step down', 'step in', 'step into', 'step on', 'step out',
    'step up', 'stick around', 'stick at', 'stick by', 'stick down',
    'stick out', 'stick to', 'stick up', 'stick up for', 'stick with',
    'stop by', 'stop in', 'stop off', 'stop out', 'stop over',
    'stop up', 'sum up', 'switch off', 'switch on', 'switch over',
    'take account of', 'take advantage of', 'take after', 'take apart',
    'take away', 'take back', 'take in', 'take off', 'take on',
    'take out', 'take over', 'take to', 'take up', 'talk down to',
    'talk into', 'talk out of', 'talk over', 'talk through', 'talk up',
    'team up', 'tell apart', 'tell off', 'tell on', 'think about',
    'think ahead', 'think back', 'think of', 'think out', 'think over',
    'think through', 'think up', 'throw away', 'throw in', 'throw off',
    'throw out', 'tie down', 'tie in', 'tie up', 'touch down',
    'touch off', 'touch on', 'touch up', 'try for', 'try in',
    'try on', 'try out', 'try up', 'turn around', 'turn away',
    'turn back', 'turn down', 'turn in', 'turn into', 'turn off',
    'turn on', 'turn out', 'turn over', 'turn to', 'turn up',
    'use up', 'warm up', 'warn off', 'wash out', 'watch out',
    'wear away', 'wear down', 'wear off', 'wear out', 'wind down',
    'wind up', 'wish for', 'withdraw from', 'work at', 'work away',
    'work in', 'work off', 'work on', 'work out', 'work through',
    'work to', 'work up', 'worry about', 'wrap up', 'write off',
    # 名词短语
    'first place', 'second place', 'third place', 'point of view',
    'side effect', 'side effects', 'by the way', 'on the other hand',
    'in the end', 'at least', 'at most', 'at first', 'at last',
    'no longer', 'no more', 'any longer', 'not any more', 'once again',
    'once more', 'over and over', 'again and again', 'back and forth',
    'every now and then', 'from time to time', 'sooner or later', 'more or less',
    'more and more', 'less and less', 'or so', 'in a way', 'in some ways',
    'in any case', 'in case of', 'in fact', 'as a matter of fact',
    'by all means', 'by no means', 'for example', 'for instance',
    'in other words', 'that is to say', 'as well', 'not only but also'
]

# 常用习语
IDIOMS = [
    'break a leg', 'cost an arm and a leg', 'piece of cake',
    'spill the beans', 'hit the hay', 'break the ice',
    'beat around the bush', 'once in a blue moon', 'under the weather',
    'on cloud nine', 'burn the midnight oil', 'kill two birds with one stone',
    'let the cat out of the bag', 'a penny for your thoughts', 'bite the bullet',
    'go the extra mile', 'when pigs fly', 'heart of gold',
    'break even', 'call it a day', 'cut to the chase',
    'get the ball rolling', 'in the nick of time', 'jump on the bandwagon',
    'keep your chin up', 'leave no stone unturned', 'make ends meet',
    'no pain no gain', 'play it by ear', 'pull yourself together',
    'see eye to eye', 'take it with a grain of salt', 'the ball is in your court',
    'turn over a new leaf', 'wake up and smell the coffee', 'you can say that again',
    'better late than never', 'every cloud has a silver lining', 'practice makes perfect',
    'actions speak louder than words', 'don t put all your eggs in one basket',
    'the early bird catches the worm', 'when in Rome do as the Romans do',
    'a picture is worth a thousand words', 'time flies when you are having fun',
    'all good things must come to an end', 'blood is thicker than water',
    'don t count your chickens before they hatch', 'haste makes waste',
    'if at first you don t succeed try try again', 'money talks',
    'necessity is the mother of invention', 'the proof is in the pudding',
    'when the going gets tough the tough get going', 'you can t judge a book by its cover',
    'a fool and his money are soon parted', 'a stitch in time saves nine',
    'birds of a feather flock together', 'curiosity killed the cat',
    'do as I say not as I do', 'easy come easy go', 'empty vessels make the most noise',
    'he who laughs last laughs longest', 'it s better to give than to receive',
    'knowledge is power', 'love conquers all', 'money can t buy happiness',
    'no man is an island', 'old habits die hard', 'opposites attract',
    'practice what you preach', 'silence is golden', 'the apple doesn t fall far from the tree',
    'there is no place like home', 'two heads are better than one',
    'variety is the spice of life', 'what goes around comes around',
    # 扩展习语
    'add insult to injury', 'Barking up the wrong tree', 'beat a dead horse',
    'bite off more than you can chew', 'break the bank', 'bring home the bacon',
    'burn the candle at both ends', 'bury the hatchet', 'call it quits',
    'can t judge a book by its cover', 'castle in the air', 'cat got your tongue',
    'chicken out', 'chip on your shoulder', 'close enough for government work',
    'costs an arm and a leg', 'cross that bridge when we come to it',
    'cry over spilled milk', 'curiosity killed the cat', 'cut to the quick',
    'dark horse', 'devil s advocate', 'die in the hills', 'dirt cheap',
    'divide and conquer', 'do the math', 'don t look a gift horse in the mouth',
    'down to the wire', 'drastic times call for drastic measures', 'drink like a fish',
    'drop the ball', 'eat like a bird', 'eat like a horse', 'every dog has his day',
    'face the music', 'fair and square', 'fall from grace', 'far cry from',
    'feast or famine', 'few and far between', 'fit as a fiddle', 'flog a dead horse',
    'fly off the handle', 'follow suit', 'fool s gold', 'for good measure',
    'get a taste of your own medicine', 'get out of hand', 'get your act together',
    'give the benefit of the doubt', 'go down in flames', 'go the distance',
    'go to pot', 'goes to show', 'good Samaritans', 'great minds think alike',
    'grow on you', 'haste makes waste', 'have a bone to pick', 'have your hands full',
    'head over heels', 'hear on the grapevine', 'hit the nail on the head',
    'hit the road', 'hit the sack', 'hold your horses', 'honest truth',
    'hook line and sinker', 'hot under the collar', 'hound dog',
    'I could care less', 'I rest my case', 'in hot water', 'in the bag',
    'in the same boat', 'in the zone', 'it goes without saying', 'it is not over till the fat lady sings',
    'jack of all trades', 'jump the gun', 'keep an eye on', 'keep your fingers crossed',
    'kill time', 'kiss and tell', 'know the ropes', 'last straw',
    'last word', 'law of the jungle', 'lay off', 'left holding the bag',
    'let bygones be bygones', 'let sleeping dogs lie', 'level playing field',
    'like a fish out of water', 'like pulling teeth', 'lion s share',
    'living on borrowed time', 'long and short of it', 'look before you leap',
    'lose heart', 'lose your head', 'lose your temper', 'low man on the totem pole',
    'make a long story short', 'make matters worse', 'man up', 'matter of fact',
    'measure twice cut once', 'meet halfway', 'method to my madness', 'middle of the road',
    'might and main', 'miss the boat', 'moment of truth', 'monkey business',
    'more harm than good', 'more than meets the eye', 'murder will out',
    'neck and neck', 'needless to say', 'new lease on life', 'new kid on the block',
    'night and day', 'nine times out of ten', 'not cricket', 'not in the same league',
    'off and on', 'off the deep end', 'off the record', 'off the top of my head',
    'on a roll', 'on cloud nine', 'on pins and needles', 'on the ball',
    'on the fence', 'on the go', 'on the hook', 'on the house',
    'on the level', 'on the money', 'on the nose', 'on the q.t.',
    'on the same page', 'on the spot', 'on the take', 'on thin ice',
    'once and for all', 'once in a while', 'one and the same', 'one foot in the grave',
    'out of hand', 'out of harm s way', 'out of line', 'out of luck',
    'out of the blue', 'out of the loop', 'out of the question', 'out of town',
    'over and done with', 'over my dead body', 'over the hill', 'over the long haul',
    'over the moon', 'over the top', 'owe someone one', 'pack rat',
    'pandora s box', 'pass the buck', 'patience is a virtue', 'pay off',
    'pick up the tab', 'pick your poison', 'pie in the sky', 'pipe dream',
    'plateau', 'play by ear', 'play second fiddle', 'play with fire',
    'plug away', 'point blank', 'poker face', 'pot calling the kettle black',
    'pretty please', 'primrose path', 'proverbially', 'pull a fast one',
    'pull punches', 'push the envelope', 'put a crimp in', 'put all your eggs in one basket',
    'put it there', 'raise the bar', 'raise the roof', 'read between the lines',
    'red herring', 'rest on your laurels', 'right off the bat', 'ring a bell',
    'rise and shine', 'rock the boat', 'rollicking', 'root beer',
    'rowdy', 'run of the mill', 'rush job', 'safety in numbers',
    'save face', 'saved by the bell', 'scrape the bottom of the barrel', 'see double',
    'sell someone down the river', 'sense and nonsense', 'set in stone', 'set the record straight',
    'seventh heaven', 'shed light', 'shoot from the hip', 'shoot the breeze',
    'short and sweet', 'short changed', 'shot in the dark', 'shut your mouth',
    'sick and tired', 'side of the track', 'sink or swim', 'six of one half dozen of the other',
    'skate on thin ice', 'sleep like a log', 'slipped my mind', 'smooth sailing',
    'snowed under', 'so far so good', 'sooner or later', 'sort of kind of',
    'speak of the devil', 'spend a penny', 'spill the beans', 'spinning my wheels',
    'splash out', 'spoil the ship for a ha pporth of tar', 'spread like wildfire',
    'square one', 'stab in the dark', 'stall for time', 'stand your ground',
    'start from scratch', 'stay on the ball', 'stay tuned', 'step up to the plate',
    'stick in the mud', 'stir up a hornet s nest', 'straw that broke the camel s back',
    'strength in numbers', 'stretch the truth', 'strike while the iron is hot',
    'strong suit', 'sugarcoat', 'swing state', 'taboo',
    'take a back seat', 'take it easy', 'take it or leave it', 'take my word for it',
    'take the bull by the horns', 'take the cake', 'take the heat', 'talk turkey',
    'tear a strip off', 'teeth and effect', 'tell it like it is', 'the best of both worlds',
    'the exception that proves the rule', 'the finer things', 'the five Ws', 'the grass is always greener',
    'the ins and outs', 'the long and short of it', 'the making of', 'the more the merrier',
    'the name of the game', 'the only game in town', 'the pen is mightier than the sword',
    'the powers that be', 'the run of the mill', 'the show must go on', 'the squeaky wheel gets the grease',
    'the way of the world', 'the write stuff', 'thick and fast', 'thick as a brick',
    'think on your feet', 'thirsty as a', 'this is the life', 'thought for the day',
    'through and through', 'through thick and thin', 'throw in the towel', 'throw the baby out with the bathwater',
    'tick all the boxes', 'tie the knot', 'time and again', 'time is of the essence',
    'time out', 'tip of the iceberg', 'to a degree', 'to be exact',
    'to be precise', 'to date', 'to err is human', 'to say the least',
    'to the best of my knowledge', 'to the contrary', 'to the core', 'to the letter',
    'to the nearest', 'to the nth degree', 'to the point', 'together with',
    'tongue in cheek', 'too big for your boots', 'too close for comfort',
    'too good to be true', 'too little too late', 'too many cooks spoil the broth',
    'top of the line', 'topsy turvy', 'touch and go', 'trial and error',
    'trials and tribulations', 'tricks of the trade', 'trickle down', 'tried and tested',
    'trillion', 'trip down memory lane', 'trip up', 'true blue',
    'true to form', 'true to type', 'turn a blind eye', 'turn over a new leaf',
    'twist of fate', 'twist someone s arm', 'two bits', 'two of a kind',
    'under pressure', 'under the circumstances', 'under the table', 'under the weather',
    'until the cows come home', 'up against', 'up and at them', 'up for grabs',
    'up in arms', 'up in the air', 'up the ante', 'up the creek',
    'up the pole', 'up the wall', 'update', 'upgrade',
    'uphill battle', 'upon my word', 'upper crust', 'upright',
    'uproar', 'upset the apple cart', 'upwardly mobile', 'use your noodle',
    'user error', 'usual suspects', 'vain attempt', 'variety is the spice of life',
    'various', 'veer off course', 'vicious circle', 'vicious cycle',
    'video', 'view to a kill', 'virtue is its own reward', 'virus',
    'vision thing', 'visit', 'visual', 'vocabulary',
    'voice of reason', 'voice', 'volatile', 'volunteer',
    'vote with their feet', 'wag the dog', 'wait and see', 'wait in the wings',
    'wait on', 'wait up for', 'wake up call', 'walk a mile in someone s shoes',
    'walk on eggshells', 'walk the talk', 'wall flower', 'wampum',
    'want ad', 'war of attrition', 'war of words', 'warm the cockles of my heart',
    'warn', 'warrant', 'warrior', 'wash my hands of',
    'waste', 'waste not want not', 'watch my dust', 'watch one s language',
    'water under the bridge', 'wave a magic wand', 'weasel out of', 'weather the storm',
    'web', 'wed', 'wee hours', 'weed out',
    'weekend', 'weigh a ton', 'weigh in', 'weigh out',
    'weight of the world', 'weird and wonderful', 'welp', 'went out of my way',
    'wet behind the ears', 'whale of a time', 'what comes around goes around', 'what in the world',
    'what is more', 'when all is said and done', 'where the rubber meets the road', 'while the going is good',
    'whip hand', 'whistle for', 'white as a sheet', 'white elephant',
    'whole ball of wax', 'whole different kettle of fish', 'whoopee', 'wicked twist of fate',
    'wide of the mark', 'wife', 'wild and woolly', 'wild goose chase',
    'will do', 'win by a nose', 'win hands down', 'win out',
    'wind in the willows', 'wind up', 'wishful thinking', 'with a grain of salt',
    'with flying colors', 'with good grace', 'with open arms', 'within an ace of',
    'without a care in the world', 'without batting an eyelid', 'without prejudice', 'witness',
    'wolf at the door', 'won hands down', 'wonder', 'wont take no for an answer',
    'wood', 'word for word', 'word of mouth', 'work a treat',
    'work like a charm', 'work my socks off', 'work out fine', 'world and all',
    'world of difference', 'world weary', 'worn out', 'worried sick',
    'worrywart', 'worse for wear', 'worsen', 'worth its weight in gold',
    'worth the candle', 'worthy', 'wound up', 'wrap my head around',
    'wrap up', 'wrath of', 'wreak havoc', 'wrestle with',
    'wring my hands', 'write in', 'write off', 'wrong end of the stick',
    'wrongful', 'yada yada', 'year in year out', 'yellow journalism',
    'you are the boss', 'you bet', 'you can say that again', 'you asked for it',
    'you better believe it', 'you couldn t pay me to', 'you never can tell', 'you re the boss',
    'yours truly', 'youthful', 'zero in on', 'zip your lip'
]

# 新闻阅读高频短语白名单
def load_news_phrase_whitelist() -> List[str]:
    """从 docs/NEWS_PHRASE_WHITELIST.md 加载新闻短语白名单。"""
    project_root = Path(__file__).resolve().parents[3]
    whitelist_path = project_root / "docs" / "NEWS_PHRASE_WHITELIST.md"
    if not whitelist_path.exists():
        return []

    phrases = []
    in_phrase_section = False
    for line in whitelist_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("## "):
            in_phrase_section = bool(re.match(r"^## [1-4]\.", line))
            continue
        if not in_phrase_section:
            continue
        if not line.startswith("- "):
            continue
        phrase = line[2:].strip().lower()
        if len(phrase.split()) >= 2:
            phrases.append(phrase)
    return phrases

NEWS_PHRASE_WHITELIST = load_news_phrase_whitelist()

# 词根词缀数据库
WORD_ROOTS = {
    'un-': {'meaning': '不，否定', 'examples': ['unhappy', 'unable', 'unknown']},
    're-': {'meaning': '再，重新', 'examples': ['return', 'review', 'rebuild']},
    'pre-': {'meaning': '前，预先', 'examples': ['preview', 'predict', 'prepare']},
    'dis-': {'meaning': '否定，相反', 'examples': ['disagree', 'disappear', 'discover']},
    'in-': {'meaning': '不，向内', 'examples': ['invisible', 'include', 'inside']},
    'im-': {'meaning': '不，向内', 'examples': ['impossible', 'import', 'improve']},
    'ex-': {'meaning': '出，外', 'examples': ['export', 'exclude', 'exit']},
    'sub-': {'meaning': '下，次', 'examples': ['subway', 'submit', 'submarine']},
    'super-': {'meaning': '超，上', 'examples': ['supermarket', 'superman', 'supervise']},
    'inter-': {'meaning': '之间，相互', 'examples': ['international', 'internet', 'interview']},
    'trans-': {'meaning': '跨越，转变', 'examples': ['transport', 'transfer', 'translate']},
    'anti-': {'meaning': '反对，抗', 'examples': ['antiwar', 'antibody', 'antivirus']},
    'auto-': {'meaning': '自动，自己', 'examples': ['automatic', 'automobile', 'autonomous']},
    'bio-': {'meaning': '生命，生物', 'examples': ['biology', 'biography', 'biodiversity']},
    'co-': {'meaning': '共同，一起', 'examples': ['cooperate', 'coexist', 'coordinate']},
    'de-': {'meaning': '向下，去除', 'examples': ['decrease', 'destroy', 'decline']},
    'mis-': {'meaning': '错误，坏', 'examples': ['mistake', 'mislead', 'misunderstand']},
    'over-': {'meaning': '过度，在上', 'examples': ['overcome', 'overlook', 'overseas']},
    'post-': {'meaning': '后', 'examples': ['postwar', 'postpone', 'postgraduate']},
    'tele-': {'meaning': '远程', 'examples': ['telephone', 'television', 'telescope']},
    '-able/-ible': {'meaning': '能够...的', 'examples': ['readable', 'visible', 'possible']},
    '-tion/-sion': {'meaning': '名词后缀，表示行为/状态', 'examples': ['action', 'decision', 'education']},
    '-ment': {'meaning': '名词后缀，表示行为/结果', 'examples': ['development', 'movement', 'agreement']},
    '-ness': {'meaning': '名词后缀，表示状态/性质', 'examples': ['happiness', 'darkness', 'kindness']},
    '-ful': {'meaning': '充满...的', 'examples': ['beautiful', 'helpful', 'powerful']},
    '-less': {'meaning': '没有...的', 'examples': ['homeless', 'careless', 'endless']},
    '-ly': {'meaning': '副词后缀', 'examples': ['quickly', 'carefully', 'happily']},
    '-er/-or': {'meaning': '做...的人/物', 'examples': ['teacher', 'actor', 'computer']},
    '-ist': {'meaning': '从事...的人', 'examples': ['artist', 'scientist', 'journalist']},
    '-ize/-ise': {'meaning': '使成为', 'examples': ['realize', 'organize', 'modernize']},
    '-ous/-ious': {'meaning': '具有...性质的', 'examples': ['famous', 'curious', 'dangerous']},
    'spect': {'meaning': '看', 'examples': ['inspect', 'respect', 'spectator']},
    'dict': {'meaning': '说', 'examples': ['predict', 'dictionary', 'contradict']},
    'port': {'meaning': '携带，运送', 'examples': ['transport', 'export', 'import']},
    'struct': {'meaning': '建造', 'examples': ['construct', 'structure', 'instruct']},
    'duct': {'meaning': '引导', 'examples': ['conduct', 'produce', 'reduce']},
    'scrib/script': {'meaning': '写', 'examples': ['describe', 'script', 'prescription']},
    'ject': {'meaning': '投掷', 'examples': ['reject', 'project', 'inject']},
    'tract': {'meaning': '拉，拖', 'examples': ['attract', 'extract', 'contract']},
    'form': {'meaning': '形状，形成', 'examples': ['transform', 'inform', 'perform']},
    'mit/miss': {'meaning': '发送', 'examples': ['transmit', 'mission', 'submit']},
}

# 语域分类
REGISTER_TERMS = {
    'academic': ['analysis', 'concept', 'theory', 'methodology', 'hypothesis', 'empirical',
                 'significant', 'substantial', 'comprehensive', 'fundamental', 'perspective',
                 'mechanism', 'phenomenon', 'implication', 'demonstration', 'correlation',
                 'predominant', 'controversy', 'paradigm', 'framework', 'validity', 'criterion',
                 'quantitative', 'qualitative', 'statistical', 'proportional', 'hierarchical',
                 'interdisciplinary', 'contextual', 'systematic', 'rigorous', 'empirical'],
    'formal': ['approximately', 'consequently', 'nevertheless', 'furthermore', 'moreover',
               'subsequently', 'predominantly', 'notwithstanding', 'accordingly', 'additionally',
               'initially', 'ultimately', 'fundamentally', 'essentially', 'significantly',
               'considerably', 'relatively', 'comparatively', 'potentially', 'apparently'],
    'informal': ['stuff', 'guy', 'thing', 'cool', 'awesome', 'chill', 'hang out', 'hit up',
                 'wanna', 'gonna', 'kinda', 'sorta', 'pretty much', 'a lot', 'really',
                 'totally', 'completely', 'absolutely', 'literally', 'actually'],
    'technical': ['algorithm', 'database', 'interface', 'parameter', 'variable', 'function',
                  'module', 'protocol', 'framework', 'architecture', 'implementation',
                  'compiler', 'debug', 'encryption', 'bandwidth', 'latency', 'server',
                  'client', 'API', 'SDK', 'framework', 'repository', 'deploy'],
    'business': ['revenue', 'profit', 'investment', 'market', 'strategy', 'competition',
                 'management', 'corporate', 'financial', 'economic', 'industry', 'consumer',
                 'shareholder', 'stakeholder', 'entrepreneur', 'startup', 'venture',
                 'negotiation', 'contract', 'agreement', 'acquisition', 'merger'],
}

def get_register(word: str) -> str:
    """判断单词的语域"""
    word_lower = word.lower()
    for register, terms in REGISTER_TERMS.items():
        if word_lower in terms:
            return register
    return 'general'

def get_word_roots(word: str) -> List[Dict]:
    """获取单词的词根词缀信息"""
    word_lower = word.lower()
    roots = []
    
    for affix, info in WORD_ROOTS.items():
        if affix.startswith('-'):  # 后缀
            if word_lower.endswith(affix[1:]):
                roots.append({
                    'affix': affix,
                    'type': 'suffix',
                    'meaning': info['meaning']
                })
        elif affix.endswith('-'):  # 前缀
            if word_lower.startswith(affix[:-1]):
                roots.append({
                    'affix': affix,
                    'type': 'prefix',
                    'meaning': info['meaning']
                })
        else:  # 词根
            if affix in word_lower:
                roots.append({
                    'affix': affix,
                    'type': 'root',
                    'meaning': info['meaning']
                })
    
    return roots

class WordExtractor:
    """词汇提取器 - 根据官方分级标准（四六级、托福）提取文章中的词汇"""

    def __init__(self):
        self.stop_words = BASIC_WORDS

    def get_word_difficulty(self, word: str) -> str:
        """
        根据官方词汇表确定单词难度
        返回: Basic, CET4, CET6, TOEFL 或 None（未分类）
        """
        word_lower = word.lower().strip()
        candidate_forms = {word_lower, *get_basic_candidate_forms(word_lower)}
        
        if candidate_forms & BASIC_WORDS:
            return "Basic"

        override_difficulties = [
            NEWS_WORD_DIFFICULTY_OVERRIDES[candidate]
            for candidate in candidate_forms
            if candidate in NEWS_WORD_DIFFICULTY_OVERRIDES
        ]
        if override_difficulties:
            difficulty_order = {"CET4": 1, "CET6": 2, "TOEFL": 3, "GRE": 4}
            return max(override_difficulties, key=lambda level: difficulty_order[level])

        if candidate_forms & CET4_ONLY_WORDS:
            return "CET4"
        elif candidate_forms & CET6_ONLY_WORDS:
            return "CET6"
        elif candidate_forms & TOEFL_ONLY_WORDS:
            return "TOEFL"
        elif candidate_forms & GRE_ONLY_WORDS:
            return "GRE"
        return None

    def extract_words(self, text: str, min_difficulty: str = "CET4") -> List[Dict]:
        """
        从文本中提取指定难度以上的单词
        :param text: 输入文本
        :param min_difficulty: 最低难度筛选 (Basic, CET4, CET6, TOEFL)
        :return: 单词列表，包含单词、难度、出现次数、语域和词根词缀
        """
        words = re.findall(r'\b[a-zA-Z]{3,}(?:-[a-zA-Z]{3,})*\b', text.lower())
        word_counts = Counter(words)
        
        difficulty_order = {"Basic": 0, "CET4": 1, "CET6": 2, "TOEFL": 3, "GRE": 4}
        min_level = difficulty_order.get(min_difficulty, 1)
        
        result = []
        for word, count in word_counts.items():
            if word in self.stop_words:
                continue
            
            difficulty = self.get_word_difficulty(word)
            if difficulty and difficulty_order.get(difficulty, 0) >= min_level:
                register = get_register(word)
                roots = get_word_roots(word)
                
                word_info = {
                    "word": word,
                    "difficulty": difficulty,
                    "count": count,
                    "register": register,
                }
                
                if roots:
                    word_info["roots"] = roots
                
                result.append(word_info)
        
        return sorted(
            result,
            key=lambda x: (
                -difficulty_order[x["difficulty"]],
                -x["count"],
                x["word"]
            )
        )

    def extract_phrases(self, text: str) -> List[Dict]:
        """
        从文本中提取常用短语和习语
        :param text: 输入文本
        :return: 短语列表
        """
        found = {}

        phrase_sources = [
            (PHRASES, "phrase"),
            (NEWS_PHRASE_WHITELIST, "phrase"),
            (IDIOMS, "idiom"),
        ]

        for phrase_list, phrase_type in phrase_sources:
            for phrase in phrase_list:
                normalized_phrase = " ".join(phrase.lower().split())
                if len(normalized_phrase.split()) < 2:
                    continue

                pattern = r'\b' + r'\s+'.join(
                    re.escape(part) for part in normalized_phrase.split()
                ) + r'\b'

                if re.search(pattern, text, flags=re.IGNORECASE):
                    existing = found.get(normalized_phrase)
                    if not existing or existing["type"] != "idiom":
                        found[normalized_phrase] = {
                            "phrase": normalized_phrase,
                            "type": phrase_type
                        }

        return sorted(
            found.values(),
            key=lambda item: (-len(item["phrase"].split()), item["phrase"])
        )

    def analyze_text(self, text: str, min_difficulty: str = "CET4") -> Dict:
        """
        综合分析文本中的词汇和短语
        :param text: 输入文本
        :param min_difficulty: 最低难度筛选
        :return: 分析结果
        """
        words = self.extract_words(text, min_difficulty)
        phrases = self.extract_phrases(text)
        
        return {
            "words": words,
            "phrases": phrases,
            "word_count": len(words),
            "phrase_count": len(phrases)
        }

# 创建全局实例
word_extractor = WordExtractor()

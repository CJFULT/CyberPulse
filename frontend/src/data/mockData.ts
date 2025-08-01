import { Article, Category } from '../types';

export const mockArticles: Article[] = [
  {
    id: '1',
    title: 'Revolutionary AI Breakthrough in Quantum Computing',
    content: 'Scientists have achieved a major breakthrough in quantum-AI hybrid systems...',
    url: 'https://example.com/ai-quantum-breakthrough',
    publishedAt: '2025-01-08T10:00:00Z',
    source: 'TechCrunch',
    category: 'artificial-intelligence',
    views: 1247,
    excerpt: 'A groundbreaking development in quantum-AI integration promises to revolutionize computing power and machine learning capabilities.'
  },
  {
    id: '2',
    title: 'Next-Gen Cybersecurity Framework Released',
    content: 'The latest cybersecurity framework addresses zero-trust architecture...',
    url: 'https://example.com/cybersecurity-framework',
    publishedAt: '2025-01-08T09:30:00Z',
    source: 'Security Weekly',
    category: 'cybersecurity',
    views: 892,
    excerpt: 'A comprehensive new framework for zero-trust security architecture is set to transform enterprise cybersecurity practices.'
  },
  {
    id: '3',
    title: 'Blockchain Adoption Surges in Enterprise',
    content: 'Major corporations are rapidly adopting blockchain technology...',
    url: 'https://example.com/blockchain-enterprise',
    publishedAt: '2025-01-08T08:45:00Z',
    source: 'CoinDesk',
    category: 'blockchain',
    views: 634,
    excerpt: 'Enterprise blockchain adoption reaches new heights as companies seek transparency and efficiency improvements.'
  },
  {
    id: '4',
    title: 'Machine Learning Models Show 99% Accuracy',
    content: 'New ML algorithms demonstrate unprecedented accuracy rates...',
    url: 'https://example.com/ml-accuracy',
    publishedAt: '2025-01-08T07:15:00Z',
    source: 'AI News',
    category: 'artificial-intelligence',
    views: 1156,
    excerpt: 'Latest machine learning breakthroughs achieve near-perfect accuracy in complex pattern recognition tasks.'
  },
  {
    id: '5',
    title: 'Critical Vulnerability Discovered in Major Framework',
    content: 'Security researchers have identified a critical vulnerability...',
    url: 'https://example.com/critical-vulnerability',
    publishedAt: '2025-01-08T06:30:00Z',
    source: 'InfoSec Today',
    category: 'cybersecurity',
    views: 2341,
    excerpt: 'A severe security flaw affecting millions of applications requires immediate attention and patching.'
  },
  {
    id: '6',
    title: 'DeFi Protocol Launches Revolutionary Features',
    content: 'The newest DeFi protocol introduces groundbreaking features...',
    url: 'https://example.com/defi-features',
    publishedAt: '2025-01-08T05:00:00Z',
    source: 'DeFi Pulse',
    category: 'blockchain',
    views: 743,
    excerpt: 'Innovation in decentralized finance continues with new protocol features that enhance user experience and security.'
  }
];

export const mockCategories: Category[] = [
  {
    id: 'artificial-intelligence',
    name: 'Artificial Intelligence',
    description: 'Latest developments in AI, ML, and neural networks',
    color: '#00D4FF',
    gradient: 'from-cyan-400 to-blue-500',
    articles: mockArticles.filter(article => article.category === 'artificial-intelligence'),
    summary: 'AI continues to push boundaries with quantum computing integration and machine learning models achieving unprecedented 99% accuracy rates. These developments signal a new era of computational power and intelligent systems that will transform industries worldwide.',
    totalViews: 2403
  },
  {
    id: 'cybersecurity',
    name: 'Cybersecurity',
    description: 'Security threats, vulnerabilities, and defense strategies',
    color: '#FF6B35',
    gradient: 'from-orange-400 to-red-500',
    articles: mockArticles.filter(article => article.category === 'cybersecurity'),
    summary: 'The cybersecurity landscape evolves rapidly with new zero-trust frameworks emerging alongside critical vulnerability discoveries. Organizations must stay vigilant as threats become more sophisticated, requiring comprehensive security strategies and immediate response protocols.',
    totalViews: 3233
  },
  {
    id: 'blockchain',
    name: 'Blockchain',
    description: 'Cryptocurrency, DeFi, and distributed ledger technology',
    color: '#9D4EDD',
    gradient: 'from-purple-400 to-pink-500',
    articles: mockArticles.filter(article => article.category === 'blockchain'),
    summary: 'Blockchain technology gains enterprise momentum with major corporations embracing distributed ledger solutions. DeFi protocols continue innovating with revolutionary features that enhance security and user experience, driving mainstream adoption forward.',
    totalViews: 1377
  }
];
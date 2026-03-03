import React, { useState } from 'react'
import { useUser } from '../../../hooks/useUser'
import { useApi } from '../../../hooks/useApi'
import { apiService } from '../../../services/api'
import { SearchResponse, SearchResult } from '../../../types'
import Card from '../../../components/ui/Card'
import Input from '../../../components/ui/Input'
import Button from '../../../components/ui/Button'
import Badge from '../../../components/ui/Badge'
import { Search, FileText, ExternalLink, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

const SearchBar: React.FC = () => {
    const { addXp } = useUser()
    const { loading, execute } = useApi()
    const [query, setQuery] = useState('')
    const [results, setResults] = useState<SearchResponse | null>(null)

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault()

        if (!query.trim()) {
            toast.error('Please enter a search query')
            return
        }

        execute(
            () => apiService.searchDocuments(query, 5),
            (response) => {
                setResults(response)
                addXp(response.xpGained)
                toast.success(`Found ${response.results.length} results! +${response.xpGained} XP`)
            }
        )
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Search Documents</h2>
                <p className="text-primary-600">
                    Find relevant information from your uploaded documents using AI-powered search
                </p>
            </div>

            {/* Search Form */}
            <Card variant="glass" className="p-6">
                <form onSubmit={handleSearch} className="space-y-4">
                    <div className="flex gap-4">
                        <Input
                            placeholder="Ask anything about your documents..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            variant="glass"
                            className="flex-1"
                            icon={<Search className="h-5 w-5" />}
                        />
                        <Button
                            type="submit"
                            variant="accent"
                            loading={loading}
                            icon={<Search className="h-5 w-5" />}
                        >
                            Search
                        </Button>
                    </div>

                    <div className="flex items-center justify-between">
                        <p className="text-sm text-primary-600">
                            Use natural language to search through all your documents
                        </p>
                        <Badge variant="accent">+2 XP per search</Badge>
                    </div>
                </form>
            </Card>

            {/* Search Results */}
            {results && (
                <Card variant="glass" className="p-6">
                    <div className="mb-6">
                        <h3 className="text-xl font-semibold text-primary-900 mb-2">
                            Search Results
                        </h3>
                        <p className="text-primary-600">
                            Found {results.results.length} results for "{results.query}"
                        </p>
                    </div>

                    <div className="space-y-4">
                        {results.results.map((result, index) => (
                            <SearchResultItem key={index} result={result} />
                        ))}
                    </div>

                    {results.results.length === 0 && (
                        <div className="text-center py-8">
                            <FileText className="h-12 w-12 text-primary-400 mx-auto mb-4" />
                            <p className="text-primary-600">No results found</p>
                            <p className="text-primary-500 text-sm mt-2">
                                Try different keywords or upload more documents
                            </p>
                        </div>
                    )}
                </Card>
            )}

            {/* Search Tips */}
            <Card variant="glass" className="p-6">
                <h3 className="text-lg font-semibold text-primary-900 mb-3">
                    Search Tips
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Use natural language</p>
                        <p className="text-primary-600 text-sm">
                            "What is machine learning?" works better than "machine learning definition"
                        </p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Be specific</p>
                        <p className="text-primary-600 text-sm">
                            Include context and details for better results
                        </p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Ask questions</p>
                        <p className="text-primary-600 text-sm">
                            Frame your queries as questions for more precise answers
                        </p>
                    </div>

                    <div className="space-y-2">
                        <p className="text-primary-900 font-medium">Explore topics</p>
                        <p className="text-primary-600 text-sm">
                            Search for themes, concepts, and relationships
                        </p>
                    </div>
                </div>
            </Card>
        </div>
    )
}

interface SearchResultItemProps {
    result: SearchResult
}

const SearchResultItem: React.FC<SearchResultItemProps> = ({ result }) => {
    return (
        <Card variant="default" className="p-4">
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-2">
                    <FileText className="h-4 w-4 text-accent-500" />
                    <Badge variant="accent" size="sm">
                        {result.source}
                    </Badge>
                    {result.page && (
                        <Badge variant="secondary" size="sm">
                            Page {result.page}
                        </Badge>
                    )}
                </div>

                <Badge variant="success" size="sm">
                    {(result.score * 100).toFixed(0)}% match
                </Badge>
            </div>

            <p className="text-primary-900 leading-relaxed mb-3">
                {result.content}
            </p>

            <div className="flex items-center justify-between">
                <p className="text-sm text-primary-600">
                    Relevance: {(result.score * 100).toFixed(1)}%
                </p>
                <Button variant="ghost" size="sm">
                    <ExternalLink className="h-4 w-4 mr-1" />
                    View Source
                </Button>
            </div>
        </Card>
    )
}

export default SearchBar

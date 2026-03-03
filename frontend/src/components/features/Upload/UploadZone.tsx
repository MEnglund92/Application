import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useUser } from '../../../hooks/useUser'
import { useApi } from '../../../hooks/useApi'
import { apiService } from '../../../services/api'
import { UploadResponse } from '../../../types'
import Card from '../../../components/ui/Card'
import Button from '../../../components/ui/Button'
import Badge from '../../../components/ui/Badge'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const UploadZone: React.FC = () => {
    const { addXp } = useUser()
    const { loading, execute } = useApi()
    const [uploadedFiles, setUploadedFiles] = useState<UploadResponse[]>([])

    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            acceptedFiles.forEach((file) => {
                if (file.size > 10 * 1024 * 1024) {
                    toast.error('File size must be less than 10MB')
                    return
                }

                execute(
                    () => apiService.uploadDocument(file),
                    (response) => {
                        setUploadedFiles(prev => [response, ...prev])
                        addXp(response.xpGained)
                        toast.success(`Uploaded ${file.name}! +${response.xpGained} XP`)
                    }
                )
            })
        },
        [execute, addXp]
    )

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'text/plain': ['.txt'],
        },
        maxSize: 10 * 1024 * 1024, // 10MB
        multiple: true,
    })

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-3xl font-bold text-primary-900 mb-2">Upload Documents</h2>
                <p className="text-primary-600">
                    Add PDF or text files to build your knowledge base
                </p>
            </div>

            {/* Upload Area */}
            <Card variant="glass" className="p-8">
                <div
                    {...getRootProps()}
                    className={`
            border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
            transition-all duration-200 hover:border-accent-500
            ${isDragActive ? 'border-accent-500 bg-accent-500/10' : 'border-primary-300'}
          `}
                >
                    <input {...getInputProps()} />

                    <div className="flex flex-col items-center space-y-4">
                        <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                            {loading ? (
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent-500"></div>
                            ) : (
                                <Upload className="h-8 w-8 text-primary-600" />
                            )}
                        </div>

                        <div>
                            <p className="text-lg font-semibold text-primary-900 mb-1">
                                {isDragActive
                                    ? 'Drop your files here'
                                    : 'Drag & drop your files here'}
                            </p>
                            <p className="text-primary-600">
                                or click to browse (PDF, TXT up to 10MB)
                            </p>
                        </div>

                        <Badge variant="accent">+10 XP per document</Badge>
                    </div>
                </div>
            </Card>

            {/* Uploaded Files */}
            {uploadedFiles.length > 0 && (
                <Card variant="glass" className="p-6">
                    <h3 className="text-xl font-semibold text-primary-900 mb-4">
                        Recently Uploaded
                    </h3>

                    <div className="space-y-3">
                        {uploadedFiles.map((file, index) => (
                            <div
                                key={index}
                                className="flex items-center justify-between p-4 rounded-lg bg-primary-100/30"
                            >
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-success/20 rounded-full flex items-center justify-center">
                                        <CheckCircle className="h-5 w-5 text-success" />
                                    </div>
                                    <div>
                                        <p className="font-medium text-primary-900">{file.filename}</p>
                                        <p className="text-sm text-primary-600">
                                            {file.chunksProcessed} chunks processed
                                        </p>
                                    </div>
                                </div>

                                <div className="flex items-center space-x-2">
                                    <Badge variant="success">+{file.xpGained} XP</Badge>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            )}

            {/* Instructions */}
            <Card variant="glass" className="p-6">
                <h3 className="text-lg font-semibold text-primary-900 mb-3">
                    How it works
                </h3>

                <div className="space-y-3">
                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-accent-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-accent-500 font-bold text-sm">1</span>
                        </div>
                        <div>
                            <p className="text-primary-900 font-medium">Upload your documents</p>
                            <p className="text-primary-600 text-sm">
                                Support for PDF and text files with automatic text extraction
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-accent-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-accent-500 font-bold text-sm">2</span>
                        </div>
                        <div>
                            <p className="text-primary-900 font-medium">Text is processed</p>
                            <p className="text-primary-600 text-sm">
                                Documents are chunked and embedded for semantic search
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-3">
                        <div className="w-8 h-8 bg-accent-500/20 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                            <span className="text-accent-500 font-bold text-sm">3</span>
                        </div>
                        <div>
                            <p className="text-primary-900 font-medium">Ready for search</p>
                            <p className="text-primary-600 text-sm">
                                Use the search feature to find relevant information instantly
                            </p>
                        </div>
                    </div>
                </div>
            </Card>
        </div>
    )
}

export default UploadZone

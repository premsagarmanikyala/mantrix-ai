import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { FileText, Download, User } from 'lucide-react'
import { userApi, aiApi } from '@/lib/api'

export default function Resume() {
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)
  const [generatedResume, setGeneratedResume] = useState<any>(null)

  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: () => userApi.getAll().then(res => res.data),
  })

  const generateMutation = useMutation({
    mutationFn: (userId: number) => aiApi.generateResume(userId),
    onSuccess: (response) => {
      // In a real app, this would return the actual resume data
      setGeneratedResume({
        userId: selectedUserId,
        status: 'generated',
        createdAt: new Date().toISOString(),
        downloadUrl: '#'
      })
    },
  })

  const handleGenerate = () => {
    if (selectedUserId) {
      generateMutation.mutate(selectedUserId)
    }
  }

  const selectedUser = users.find(u => u.id === selectedUserId)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Resume Builder</h1>
        <p className="mt-2 text-gray-600 dark:text-gray-300">
          Generate AI-powered resumes based on user profiles and projects
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Selection */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Select User
          </h2>
          
          <div className="space-y-3">
            {users.map((user) => (
              <div
                key={user.id}
                onClick={() => setSelectedUserId(user.id)}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                  selectedUserId === user.id
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center">
                      <User className="h-5 w-5 text-gray-600 dark:text-gray-300" />
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {user.full_name}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      @{user.username} • {user.email}
                    </p>
                    {user.bio && (
                      <p className="text-sm text-gray-600 dark:text-gray-300 mt-1">
                        {user.bio}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {selectedUserId && (
            <div className="mt-6">
              <button
                onClick={handleGenerate}
                disabled={generateMutation.isPending}
                className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <FileText className="h-4 w-4 mr-2" />
                {generateMutation.isPending ? 'Generating...' : 'Generate Resume'}
              </button>
            </div>
          )}
        </div>

        {/* Resume Preview */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
            Resume Preview
          </h2>

          {!generatedResume && !selectedUser && (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                No resume generated
              </h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Select a user and click generate to create a resume.
              </p>
            </div>
          )}

          {selectedUser && !generatedResume && (
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6">
              <div className="text-center">
                <FileText className="mx-auto h-8 w-8 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                  Ready to generate resume for {selectedUser.full_name}
                </h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  Click the generate button to create an AI-powered resume.
                </p>
              </div>
            </div>
          )}

          {generatedResume && selectedUser && (
            <div className="space-y-4">
              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <FileText className="h-5 w-5 text-green-400" />
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-green-800 dark:text-green-200">
                      Resume Generated Successfully
                    </h3>
                    <div className="mt-2 text-sm text-green-700 dark:text-green-300">
                      <p>Resume for {selectedUser.full_name} has been generated using AI.</p>
                      <p className="mt-1">Generated at: {new Date(generatedResume.createdAt).toLocaleString()}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 dark:text-white mb-2">Resume Contents:</h4>
                <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                  <li>• Personal Information & Contact Details</li>
                  <li>• Professional Summary</li>
                  <li>• Skills & Technologies</li>
                  <li>• Project Experience</li>
                  <li>• Professional Experience</li>
                  <li>• Education & Certifications</li>
                </ul>
              </div>

              <button
                className="w-full inline-flex justify-center items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-600"
              >
                <Download className="h-4 w-4 mr-2" />
                Download Resume PDF
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
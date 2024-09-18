'use client';

import { useState } from 'react';
import CreatePresentation from "@/actions/create-presentation";

export default function Page() {
  const [isLoading, setIsLoading] = useState(false);

  const handleCreatePresentation = async () => {
    setIsLoading(true);
    try {
      await CreatePresentation();
      // The server action will handle the redirection
    } catch (error) {
      console.error('Error creating presentation:', error);
      // Optionally, you can add error handling UI here
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-screen bg-gradient-to-br from-secondary-500 to-primary-500 flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl w-full space-y-8 text-center">
        <h1 className="text-5xl sm:text-6xl md:text-7xl font-extrabold text-white">
          Welcome to Shiro AI
        </h1>
        <p className="mt-6 text-xl sm:text-2xl text-gray-200">
          Create stunning presentations with the power of AI. <br/> Like ChatGPT meets PowerPoint.
        </p>
        <div className="mt-10">
          <button
            onClick={handleCreatePresentation}
            disabled={isLoading}
            className="px-8 py-4 text-lg font-semibold rounded-full text-white bg-secondary-500 hover:bg-secondary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition duration-150 ease-in-out"
          >
            {isLoading ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating...
              </>
            ) : (
              'Create New Presentation'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

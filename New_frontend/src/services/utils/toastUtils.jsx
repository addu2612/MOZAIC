import { toast } from 'react-hot-toast';

/**
 * Display a custom error toast with validation details
 * @param {Object} error - The error object from API response
 */
export const showValidationErrors = (error) => {
  const errorData = error.response?.data?.error || error.response?.data;
  
  if (!errorData) {
    toast.error('An unexpected error occurred. Please try again.');
    return;
  }

  // Check if there are validation details
  if (errorData.details && Array.isArray(errorData.details) && errorData.details.length > 0) {
    // Create custom toast with styled validation errors
    toast.custom(
      (t) => (
        <div
          className={`${
            t.visible ? 'animate-enter' : 'animate-leave'
          } max-w-md w-full bg-white shadow-2xl rounded-lg pointer-events-auto flex flex-col border border-red-100`}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-4 pb-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0">
                <svg
                  className="w-6 h-6 text-red-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-gray-900">
                  {errorData.message || 'Validation Failed'}
                </h3>
              </div>
            </div>
            <button
              onClick={() => toast.dismiss(t.id)}
              className="flex-shrink-0 ml-4 text-gray-400 hover:text-gray-600 focus:outline-none"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          </div>

          {/* Error Details List */}
          <div className="p-4 max-h-64 overflow-y-auto">
            <ul className="space-y-2">
              {errorData.details.map((detail, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-red-500 mt-1.5"></span>
                  <span className="text-gray-700 flex-1">{detail}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      ),
      {
        duration: 6000,
        position: 'top-right',
      }
    );
  } else {
    // Single error message
    const errorMessage = errorData.message || error.message || 'An error occurred';
    toast.error(errorMessage, {
      duration: 4000,
      position: 'top-right',
      style: {
        background: '#fff',
        color: '#374151',
        border: '1px solid #fee',
        padding: '16px',
        borderRadius: '8px',
      },
      iconTheme: {
        primary: '#ef4444',
        secondary: '#fff',
      },
    });
  }
};

/**
 * Display a success toast with custom styling
 * @param {string} message - Success message to display
 */
export const showSuccessToast = (message) => {
  toast.success(message, {
    duration: 4000,
    position: 'top-right',
    style: {
      background: '#fff',
      color: '#374151',
      border: '1px solid #d1fae5',
      padding: '16px',
      borderRadius: '8px',
    },
    iconTheme: {
      primary: '#10b981',
      secondary: '#fff',
    },
  });
};

/**
 * Display a loading toast with custom styling
 * @param {string} message - Loading message to display
 * @returns {string} Toast ID
 */
export const showLoadingToast = (message) => {
  return toast.loading(message, {
    position: 'top-right',
    style: {
      background: '#fff',
      color: '#374151',
      border: '1px solid #e5e7eb',
      padding: '16px',
      borderRadius: '8px',
    },
  });
};

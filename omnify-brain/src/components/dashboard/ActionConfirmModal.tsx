'use client';

import { useState } from 'react';

interface ActionConfirmModalProps {
  action: {
    id: string;
    type: string;
    title: string;
    description: string;
    impact: string;
    urgency: 'high' | 'medium' | 'low';
  };
  onConfirm: () => Promise<void>;
  onCancel: () => void;
}

export function ActionConfirmModal({ action, onConfirm, onCancel }: ActionConfirmModalProps) {
  const [isExecuting, setIsExecuting] = useState(false);
  const [error, setError] = useState('');

  const handleConfirm = async () => {
    setIsExecuting(true);
    setError('');

    try {
      await onConfirm();
      // Modal will be closed by parent component
    } catch (err: any) {
      setError(err.message || 'Failed to execute action');
    } finally {
      setIsExecuting(false);
    }
  };

  const urgencyColors = {
    high: 'bg-red-100 text-red-800 border-red-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    low: 'bg-blue-100 text-blue-800 border-blue-300',
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-2">Confirm Action</h3>
        
        <div className="mb-4">
          <p className="text-gray-700 font-medium mb-2">{action.title}</p>
          <p className="text-sm text-gray-600 mb-4">{action.description}</p>
          
          <div className="flex items-center gap-4 mb-4">
            <div>
              <span className="text-xs text-gray-500">Expected Impact</span>
              <p className="text-sm font-medium text-green-600">{action.impact}</p>
            </div>
            <div>
              <span className="text-xs text-gray-500">Urgency</span>
              <span className={`inline-block px-2 py-1 rounded text-xs font-medium border ${urgencyColors[action.urgency]}`}>
                {action.urgency.toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-4 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
            {error}
          </div>
        )}

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={isExecuting}
            className="flex-1 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={isExecuting}
            className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 ${
              action.urgency === 'high'
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {isExecuting ? 'Executing...' : 'Execute Action'}
          </button>
        </div>
      </div>
    </div>
  );
}

